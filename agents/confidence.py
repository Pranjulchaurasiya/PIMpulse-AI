import logging
from typing import Dict, Any, List, Optional
from config import settings
from state import (
    ProductProfile,
    AttributeValue,
    UNSPSCClassification,
    ConfidenceBreakdown
)

logger = logging.getLogger("pimpulse.confidence")

def calculate_mathematical_confidence(
    mandatory_attrs: List[str],
    extracted_attrs: Dict[str, Any],
    grounding_ratio: float,
    retrieval_agreement_rate: float,
    vector_store_empty: bool,
    vision_agreement_rate: float,
    taxonomy_confidence: float,
    vision_conflicts: List[str],
    ambiguity_flag: bool = False
) -> Dict[str, Any]:
    """
    Pure deterministic mathematical confidence scoring.
    No LLM self-report or subjective hallucinations.
    Includes ambiguity penalty (0.25) when brand and MPN are missing.
    """
    # 1. Attribute Coverage: found mandatory / total mandatory with valid non-null values
    INVALID_VALUES = {"", "none", "null", "n/a", "unknown", "none/not specified", "unspecified"}
    found_count = 0
    current_keys = set(extracted_attrs.keys())
    for req in mandatory_attrs:
        for k in current_keys:
            if req in k or k in req:
                val = extracted_attrs[k]
                v_str = str(val.get("value", "") if isinstance(val, dict) else val).strip().lower()
                if v_str and v_str not in INVALID_VALUES:
                    found_count += 1
                    break
                    
    coverage = round(found_count / max(len(mandatory_attrs), 1), 3)

    # 2. Base weights calculation & Cold-start redistribution
    weights = dict(settings.BASE_WEIGHTS)
    retrieval_excluded = False
    
    # Generic ambiguous inputs without brand/MPN cap taxonomy specificity at 0.70
    effective_tax_conf = min(taxonomy_confidence, 0.70) if ambiguity_flag else taxonomy_confidence

    if vector_store_empty:
        # Cold start fix: drop retrieval_agreement and redistribute 0.15 proportionally to other 4
        retrieval_excluded = True
        remaining_keys = ["coverage", "grounding", "vision_match", "taxonomy"]
        sum_remaining = sum(weights[k] for k in remaining_keys)  # 0.85
        
        redistributed_weights = {}
        for k in remaining_keys:
            redistributed_weights[k] = round(weights[k] / sum_remaining, 4)
        redistributed_weights["retrieval_agreement"] = 0.0
        active_weights = redistributed_weights
    else:
        active_weights = weights

    # 3. Weighted Sum
    weighted_sum = (
        active_weights.get("coverage", 0.0) * coverage +
        active_weights.get("grounding", 0.0) * grounding_ratio +
        active_weights.get("retrieval_agreement", 0.0) * (0.0 if retrieval_excluded else retrieval_agreement_rate) +
        active_weights.get("vision_match", 0.0) * vision_agreement_rate +
        active_weights.get("taxonomy", 0.0) * effective_tax_conf
    )

    # 4. Conflict & Ambiguity Penalties
    total_penalty = round(len(vision_conflicts) * settings.CONFLICT_PENALTY, 3)
    ambiguity_penalty = 0.25 if ambiguity_flag else 0.0

    # 5. Final Score
    raw_calc = weighted_sum - total_penalty - ambiguity_penalty
    if effective_tax_conf <= 0.15:
        # Unclassified / gibberish inputs must not score high confidence
        final_score = max(0.0, min(0.20, raw_calc * 0.20))
    else:
        final_score = max(0.0, min(1.0, raw_calc))
    confidence_pct = round(final_score * 100.0, 2)

    return {
        "coverage": round(coverage, 3),
        "grounding_ratio": round(grounding_ratio, 3),
        "retrieval_agreement": round(0.0 if retrieval_excluded else retrieval_agreement_rate, 3),
        "retrieval_agreement_excluded": retrieval_excluded,
        "vision_match": round(vision_agreement_rate, 3),
        "taxonomy_confidence": round(effective_tax_conf, 3),
        "conflict_penalty": total_penalty,
        "ambiguity_penalty": ambiguity_penalty,
        "ambiguity_flag": ambiguity_flag,
        "confidence_pct": confidence_pct,
        "weights_used": active_weights
    }

def build_final_product_profile(
    raw_input: str,
    standardized_title: str,
    taxonomy_path: List[str],
    unspsc_code: str,
    unspsc_segment: str,
    unspsc_family: str,
    unspsc_class: str,
    extracted_attrs: Dict[str, Any],
    grounded_flags: Dict[str, bool],
    marketing_description: str,
    feature_bullets: List[str],
    vision_agreement_rate: float,
    vision_conflicts: List[str],
    confidence_breakdown: Dict[str, Any],
    evaluator_decision: str,
    provenance: Dict[str, str],
    ambiguity_flag: bool = False,
    cached: bool = False,
    latency_ms: Optional[float] = None
) -> ProductProfile:
    """
    Constructs and validates the final ProductProfile using strict Pydantic V2 schema.
    """
    attributes_dict = {}
    for k, v in extracted_attrs.items():
        if isinstance(v, dict):
            attributes_dict[k] = AttributeValue(
                value=str(v.get("value", "")),
                unit=v.get("unit"),
                source=v.get("source", "extracted"),
                grounded=grounded_flags.get(k, False),
                confidence=float(v.get("confidence", 0.95)),
                source_snippet=v.get("source_snippet")
            )
        else:
            attributes_dict[k] = AttributeValue(
                value=str(v),
                grounded=grounded_flags.get(k, False)
            )

    taxonomy = UNSPSCClassification(
        code=unspsc_code or "00000000",
        segment=unspsc_segment or "Industrial",
        family=unspsc_family or "Equipment",
        class_name=unspsc_class or "General",
        path=taxonomy_path or ["Industrial", "General"]
    )

    confidence = ConfidenceBreakdown(**confidence_breakdown)

    return ProductProfile(
        raw_input=raw_input,
        standardized_title=standardized_title or raw_input,
        taxonomy=taxonomy,
        attributes=attributes_dict,
        marketing_description=marketing_description or f"Industrial component profile for {raw_input}",
        feature_bullets=feature_bullets or [],
        vision_agreement_rate=vision_agreement_rate,
        vision_conflicts=vision_conflicts,
        ambiguity_flag=ambiguity_flag,
        confidence=confidence,
        evaluator_decision=evaluator_decision,
        provenance=provenance or {},
        cached=cached,
        latency_ms=latency_ms
    )

def classify_attribute_confidence_tier(
    attr_name: str,
    value: str,
    is_verbatim_grounded: bool,
    source_authority_tier: str,
    has_conflict: bool = False
) -> Dict[str, Any]:
    """
    Classifies an attribute into Enterprise Trust Tiers:
      Tier A: Autopublish (Verbatim OEM grounded + no conflicts)
      Tier B: Spot-check (Single OEM source, verified domain)
      Tier C: Review Required (Distributor source or conflict detected)
      Tier D: Rejected/Null (Failed grounding gate)
    """
    if not value or str(value).strip().lower() in ("", "null", "none", "n/a", "unknown"):
        return {"tier": "D", "action": "REJECTED_NULL", "description": "Null or ungrounded value emitted"}

    if is_verbatim_grounded and source_authority_tier in ("oem_pdf", "oem_web") and not has_conflict:
        return {"tier": "A", "action": "AUTOPUBLISH", "description": "Verbatim OEM grounded without conflicts"}

    if is_verbatim_grounded and source_authority_tier == "distributor" and not has_conflict:
        return {"tier": "B", "action": "SPOT_CHECK", "description": "Authorized distributor grounded; 5% audit sample"}

    return {"tier": "C", "action": "REVIEW_REQUIRED", "description": "Distributor/marketplace source or conflict detected"}

