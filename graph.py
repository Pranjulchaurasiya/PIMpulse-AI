import time
import asyncio
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from state import ProductState
from cache import semantic_cache
from agents.taxonomy import classify_taxonomy_pre, classify_taxonomy_refine, classify_taxonomy_pre_hybrid
from agents.hyde import expand_query_hyde
from agents.retrieval import retrieve_and_fuse
from agents.grading import grade_documents_batched
from agents.extraction import extract_attributes_targeted
from agents.grounding import check_attributes_grounding
from agents.vision import vision_describe, reconcile_vision_with_text
from agents.auditor import audit_enrichment_state
from agents.confidence import calculate_mathematical_confidence, build_final_product_profile

from agents.unilog_rules import sanitize_raw_industrial_input

logger = logging.getLogger("pimpulse.graph")

def _create_log_entry(node_name: str, status: str, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        "timestamp": time.time(),
        "node": node_name,
        "status": status,
        "message": message,
        "details": details or {}
    }

# -------------------------------------------------------------
# Node Definitions
# -------------------------------------------------------------

async def node_taxonomy_pre(state: ProductState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "")
    sanitized = sanitize_raw_industrial_input(raw_input)
    clean_input = sanitized["cleaned_text"] or raw_input

    t0 = time.perf_counter()
    tax_res = await classify_taxonomy_pre_hybrid(clean_input)
    dur_ms = round((time.perf_counter() - t0) * 1000, 2)
    
    prod_type_str = f" ({tax_res.get('product_type')})" if tax_res.get('product_type') else ""
    log = _create_log_entry(
        "TAXONOMY_PRE",
        "COMPLETED",
        f"Taxonomy classified -> {tax_res['class_name']}{prod_type_str} [{tax_res['unspsc_code']}] with confidence {tax_res['confidence']:.2f} in {dur_ms}ms",
        tax_res
    )
    
    return {
        "taxonomy_path": tax_res["path"],
        "unspsc_code": tax_res["unspsc_code"],
        "unspsc_segment": tax_res["segment"],
        "unspsc_family": tax_res["family"],
        "unspsc_class": tax_res["class_name"],
        "taxonomy_confidence": tax_res["confidence"],
        "taxonomy_pre_confidence": tax_res.get("taxonomy_pre_confidence", tax_res["confidence"]),
        "taxonomy_pre_unspsc_code": tax_res.get("taxonomy_pre_unspsc_code", tax_res["unspsc_code"]),
        "mandatory_attrs": tax_res["mandatory_attrs"],
        "agent_logs": [log]
    }

async def node_hyde(state: ProductState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "")
    class_name = state.get("unspsc_class", "Industrial Part")
    sanitized = sanitize_raw_industrial_input(raw_input)
    
    # If search_query already rewritten by auditor retry, keep it
    if state.get("retry_count", 0) > 0 and state.get("search_query"):
        search_query = state["search_query"]
        is_expanded = False
        hypothesis = None
    else:
        clean_input = sanitized["cleaned_text"] or raw_input
        prefix = f"{sanitized['inferred_brand']} {sanitized['normalized_mpn']}".strip()
        search_target = f"{prefix} {clean_input}".strip() if prefix and prefix not in clean_input else clean_input
        search_query, hypothesis, is_expanded = await expand_query_hyde(search_target, class_name)
    
    msg = f"HyDE expanded query ({len(search_query)} chars)" if is_expanded else "Short query expansion skipped (sufficient vocabulary)"
    log = _create_log_entry(
        "HYDE",
        "COMPLETED",
        msg,
        {"expanded_query": search_query, "hypothesis": hypothesis}
    )
    
    return {
        "search_query": search_query,
        "hyde_hypothesis": hypothesis,
        "agent_logs": [log]
    }

async def node_retrieval(state: ProductState) -> Dict[str, Any]:
    search_query = state.get("search_query", state.get("raw_input", ""))
    retrieval_res = await retrieve_and_fuse(search_query)
    
    fused_chunks = retrieval_res["retrieved_chunks"]
    web_cnt = retrieval_res["web_count"]
    vec_cnt = retrieval_res["vector_count"]
    is_empty = retrieval_res["vector_store_empty"]
    
    log = _create_log_entry(
        "RETRIEVAL_RRF",
        "COMPLETED",
        f"Fused {len(fused_chunks)} chunks via RRF (Web: {web_cnt}, Vector: {vec_cnt}, Cold-start store: {is_empty})",
        {
            "num_chunks": len(fused_chunks),
            "vector_store_empty": is_empty,
            "sample_titles": [c.get("title", "") for c in fused_chunks[:3]]
        }
    )
    
    return {
        "retrieved_chunks": fused_chunks,
        "vector_store_empty": is_empty,
        "agent_logs": [log]
    }

async def node_vision(state: ProductState) -> Dict[str, Any]:
    image_path = state.get("image_path")
    v_res = await vision_describe(image_path)
    
    msg = "Independent vision attributes extracted" if v_res["image_present"] else "No image supplied, vision branch neutral"
    log = _create_log_entry(
        "VISION_DESCRIBE",
        "COMPLETED",
        msg,
        v_res["vision_raw_attrs"]
    )
    
    return {
        "vision_raw_attrs": v_res["vision_raw_attrs"],
        "agent_logs": [log]
    }

async def node_grading(state: ProductState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "")
    search_query = state.get("search_query", raw_input)
    chunks = state.get("retrieved_chunks", [])
    mandatory = state.get("mandatory_attrs", [])
    
    graded = await grade_documents_batched(raw_input, search_query, chunks, mandatory)
    
    log = _create_log_entry(
        "DOC_GRADING",
        "COMPLETED",
        f"Batched 1-call grading passed {len(graded)}/{len(chunks)} chunks",
        {"passed_count": len(graded), "total_candidates": len(chunks)}
    )
    
    return {
        "graded_chunks": graded,
        "agent_logs": [log]
    }

async def node_extraction(state: ProductState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "")
    class_name = state.get("unspsc_class", "General")
    mandatory = state.get("mandatory_attrs", [])
    graded = state.get("graded_chunks", [])
    
    try:
        ext_res = await extract_attributes_targeted(raw_input, class_name, mandatory, graded)
        extracted = ext_res.get("extracted_attrs", {})
        ambiguity_flag = ext_res.get("ambiguity_flag", False)
        
        ambig_str = " [AMBIGUOUS: Missing Brand/MPN]" if ambiguity_flag else ""
        log = _create_log_entry(
            "EXTRACTION",
            "COMPLETED",
            f"Extracted {len(extracted)} structured attributes targeted for '{class_name}'{ambig_str}",
            {"extracted_keys": list(extracted.keys()), "ambiguity_flag": ambiguity_flag}
        )
        
        return {
            "extracted_attrs": extracted,
            "standardized_title": ext_res.get("standardized_title", raw_input),
            "marketing_description": ext_res.get("marketing_description", ""),
            "feature_bullets": ext_res.get("feature_bullets", []),
            "provenance": ext_res.get("provenance", {}),
            "ambiguity_flag": ambiguity_flag,
            "agent_logs": [log]
        }
    except Exception as exc:
        logger.error(f"Multi-model failover extraction exception caught safely: {exc}")
        log = _create_log_entry(
            "EXTRACTION",
            "UNCLASSIFIED_FAILOVER",
            f"Extraction failover caught unhandled exception ({exc}). Emitted UNCLASSIFIED safety state.",
            {"error": str(exc)}
        )
        return {
            "extracted_attrs": {},
            "standardized_title": raw_input,
            "marketing_description": f"Unclassified product profile for '{raw_input}'",
            "feature_bullets": [],
            "provenance": {"failover_error": str(exc)},
            "ambiguity_flag": True,
            "agent_logs": [log]
        }

async def node_grounding(state: ProductState) -> Dict[str, Any]:
    extracted = state.get("extracted_attrs", {})
    chunks = state.get("graded_chunks", []) or state.get("retrieved_chunks", [])
    
    ok, ratio, flags = check_attributes_grounding(extracted, chunks)
    
    log = _create_log_entry(
        "GROUNDING_CHECK",
        "COMPLETED",
        f"Deterministic substring/fuzzy check: {sum(flags.values())}/{len(flags)} attributes grounded (Ratio: {ratio:.2f})",
        {"grounding_ok": ok, "grounding_ratio": ratio, "flags": flags}
    )
    
    return {
        "grounding_ok": ok,
        "grounding_ratio": ratio,
        "grounded_flags": flags,
        "agent_logs": [log]
    }

async def node_reconcile_vision(state: ProductState) -> Dict[str, Any]:
    vision_attrs = state.get("vision_raw_attrs", {})
    extracted = state.get("extracted_attrs", {})
    image_present = bool(state.get("image_path"))
    
    rate, conflicts = reconcile_vision_with_text(vision_attrs, extracted, image_present)
    
    log = _create_log_entry(
        "RECONCILE_VISION",
        "COMPLETED",
        f"Vision-language agreement rate: {rate:.2f} ({len(conflicts)} conflicts)",
        {"vision_agreement_rate": rate, "conflicts": conflicts}
    )
    
    return {
        "vision_agreement_rate": rate,
        "vision_conflicts": conflicts,
        "agent_logs": [log]
    }

async def node_taxonomy_refine(state: ProductState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "")
    extracted = state.get("extracted_attrs", {})
    pre_score = state.get("taxonomy_pre_confidence", state.get("taxonomy_confidence", 0.5))
    unspsc_code = state.get("taxonomy_pre_unspsc_code", state.get("unspsc_code", "00000000"))
    
    refined_res, final_conf = classify_taxonomy_refine(raw_input, extracted, pre_score, unspsc_code)
    
    log = _create_log_entry(
        "TAXONOMY_REFINE",
        "COMPLETED",
        f"Taxonomy refined score: {final_conf:.2f} (pre-score: {pre_score:.2f}, code: {refined_res.get('unspsc_code', unspsc_code)})",
        {"final_confidence": final_conf, "taxonomy": refined_res}
    )
    
    return {
        "taxonomy_confidence": final_conf,
        "unspsc_code": refined_res.get("unspsc_code", unspsc_code),
        "taxonomy_path": refined_res.get("path", state.get("taxonomy_path", [])),
        "unspsc_segment": refined_res.get("segment", state.get("unspsc_segment", "General")),
        "unspsc_family": refined_res.get("family", state.get("unspsc_family", "General")),
        "unspsc_class": refined_res.get("class_name", state.get("unspsc_class", "Unclassified")),
        "agent_logs": [log]
    }

async def node_auditor(state: ProductState) -> Dict[str, Any]:
    extracted = state.get("extracted_attrs", {})
    mandatory = state.get("mandatory_attrs", [])
    grounding_ok = state.get("grounding_ok", False)
    grounding_ratio = state.get("grounding_ratio", 0.0)
    vision_agreement = state.get("vision_agreement_rate", 1.0)
    retry_count = state.get("retry_count", 0)
    raw_input = state.get("raw_input", "")
    ambiguity_flag = state.get("ambiguity_flag", False)
    unspsc_code = state.get("unspsc_code", state.get("taxonomy_pre_unspsc_code", ""))
    
    audit_res = audit_enrichment_state(
        extracted, mandatory, grounding_ok, grounding_ratio, vision_agreement, retry_count, raw_input, ambiguity_flag, unspsc_code
    )
    
    decision = audit_res["evaluator_decision"]
    notes = audit_res["audit_notes"]
    
    log = _create_log_entry(
        "AUDITOR_GATE",
        "COMPLETED",
        f"Auditor Decision: '{decision.upper()}' — {notes}",
        audit_res
    )
    
    return {
        "evaluator_decision": decision,
        "missing_mandatory_attrs": audit_res["missing_mandatory_attrs"],
        "search_query": audit_res["new_search_query"],
        "audit_notes": notes,
        "retry_count": retry_count + 1 if decision == "retry" else retry_count,
        "agent_logs": [log]
    }

async def node_confidence_and_report(state: ProductState) -> Dict[str, Any]:
    mandatory = state.get("mandatory_attrs", [])
    extracted = state.get("extracted_attrs", {})
    grounding_ratio = state.get("grounding_ratio", 0.0)
    retrieval_rate = state.get("retrieval_agreement_rate", 0.0)
    vector_store_empty = state.get("vector_store_empty", True)
    vision_agreement = state.get("vision_agreement_rate", 1.0)
    tax_conf = state.get("taxonomy_confidence", 0.5)
    conflicts = state.get("vision_conflicts", [])
    ambiguity_flag = state.get("ambiguity_flag", False)
    
    conf_breakdown = calculate_mathematical_confidence(
        mandatory, extracted, grounding_ratio, retrieval_rate, vector_store_empty, vision_agreement, tax_conf, conflicts, ambiguity_flag
    )
    
    profile = build_final_product_profile(
        raw_input=state.get("raw_input", ""),
        standardized_title=state.get("standardized_title", ""),
        taxonomy_path=state.get("taxonomy_path", []),
        unspsc_code=state.get("unspsc_code", ""),
        unspsc_segment=state.get("unspsc_segment", ""),
        unspsc_family=state.get("unspsc_family", ""),
        unspsc_class=state.get("unspsc_class", ""),
        extracted_attrs=extracted,
        grounded_flags=state.get("grounded_flags", {}),
        marketing_description=state.get("marketing_description", ""),
        feature_bullets=state.get("feature_bullets", []),
        vision_agreement_rate=vision_agreement,
        vision_conflicts=conflicts,
        confidence_breakdown=conf_breakdown,
        evaluator_decision=state.get("evaluator_decision", "accept"),
        provenance=state.get("provenance", {}),
        ambiguity_flag=ambiguity_flag,
        cached=False
    )
    
    # Save to semantic cache
    profile_dict = profile.model_dump()
    semantic_cache.set(state.get("raw_input", ""), profile_dict)
    
    log = _create_log_entry(
        "CONFIDENCE_MATH",
        "COMPLETED",
        f"Computed deterministic confidence: {conf_breakdown['confidence_pct']}% (Coverage: {conf_breakdown['coverage']}, Grounding: {conf_breakdown['grounding_ratio']}, Taxonomy: {conf_breakdown['taxonomy_confidence']})",
        conf_breakdown
    )
    
    return {
        "confidence_breakdown": conf_breakdown,
        "final_profile": profile_dict,
        "agent_logs": [log]
    }

# -------------------------------------------------------------
# Conditional Edge Router
# -------------------------------------------------------------

def route_after_audit(state: ProductState) -> Literal["retrieve_and_fuse", "confidence_and_report"]:
    decision = state.get("evaluator_decision", "accept")
    if decision == "retry":
        return "retrieve_and_fuse"
    return "confidence_and_report"

# -------------------------------------------------------------
# Compile LangGraph Workflow
# -------------------------------------------------------------

def build_pimpulse_graph():
    workflow = StateGraph(ProductState)

    # Add Nodes
    workflow.add_node("taxonomy_pre", node_taxonomy_pre)
    workflow.add_node("hyde", node_hyde)
    workflow.add_node("retrieve_and_fuse", node_retrieval)
    workflow.add_node("vision_describe", node_vision)
    workflow.add_node("grade_documents", node_grading)
    workflow.add_node("extract_attributes", node_extraction)
    workflow.add_node("check_grounding", node_grounding)
    workflow.add_node("reconcile_vision", node_reconcile_vision)
    workflow.add_node("taxonomy_refine", node_taxonomy_refine)
    workflow.add_node("auditor", node_auditor)
    workflow.add_node("confidence_and_report", node_confidence_and_report)

    # Connect Edges — Linear pipeline with vision as early parallel write-to-state
    workflow.set_entry_point("taxonomy_pre")
    workflow.add_edge("taxonomy_pre", "hyde")
    
    # Parallel Fan-Out from HyDE: both run concurrently
    # vision_describe writes vision_raw_attrs to state then terminates (no downstream edge)
    # retrieve_and_fuse continues the main text branch
    workflow.add_edge("hyde", "retrieve_and_fuse")
    workflow.add_edge("hyde", "vision_describe")
    
    # Text Retrieval Branch (linear chain — no fan-in issues)
    workflow.add_edge("retrieve_and_fuse", "grade_documents")
    workflow.add_edge("grade_documents", "extract_attributes")
    workflow.add_edge("extract_attributes", "check_grounding")
    
    # After grounding completes, reconcile reads vision state already written
    # NO fan-in edge from vision_describe — it writes to state independently
    workflow.add_edge("check_grounding", "reconcile_vision")
    workflow.add_edge("vision_describe", END)  # Vision branch terminates independently
    
    workflow.add_edge("reconcile_vision", "taxonomy_refine")
    workflow.add_edge("taxonomy_refine", "auditor")
    
    # Conditional retry or accept
    workflow.add_conditional_edges(
        "auditor",
        route_after_audit,
        {
            "retrieve_and_fuse": "retrieve_and_fuse",
            "confidence_and_report": "confidence_and_report"
        }
    )
    
    workflow.add_edge("confidence_and_report", END)

    return workflow.compile()

# Global compiled graph
pimpulse_pipeline = build_pimpulse_graph()
