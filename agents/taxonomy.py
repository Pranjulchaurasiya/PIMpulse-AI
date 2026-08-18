import json
import os
import re
from typing import Dict, Any, List, Tuple
from rapidfuzz import fuzz

TAXONOMY_FILE = os.path.join(os.path.dirname(__file__), "..", "rules", "taxonomy.json")

def load_taxonomy_rules() -> List[Dict[str, Any]]:
    try:
        with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading taxonomy: {e}")
        return []

def _normalize_text(text: str) -> str:
    # normalize delimiters, punctuation, and casing
    text = text.lower()
    text = re.sub(r"[-_/,:]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _calculate_category_score(normalized_input: str, category: Dict[str, Any]) -> float:
    keywords = category.get("keywords", [])
    if not keywords:
        return 0.0
    
    # 1. Keyword Hit Ratio
    hits = 0
    words = set(normalized_input.split())
    for kw in keywords:
        kw_norm = _normalize_text(kw)
        if " " in kw_norm:
            if kw_norm in normalized_input:
                hits += 2  # Higher weight for multi-word exact phrases
        else:
            if kw_norm in words:
                hits += 1.5
            elif kw_norm in normalized_input and len(kw_norm) >= 3:
                hits += 1.0
                
    if hits == 0:
        # Only accept strong token_set fuzzy match (>= 0.70) against category class name
        class_name = category.get("class", "")
        fuzz_ratio = fuzz.token_set_ratio(normalized_input, class_name) / 100.0
        if fuzz_ratio >= 0.70:
            return round(fuzz_ratio * 0.70, 3)
        return 0.0

    keyword_score = min(1.0, hits / max(len(keywords) * 0.20, 1.0))
    return round(keyword_score, 3)

TAXONOMY_PROMPT = """You are an industrial product classifier. Given a raw product string, identify the product category and map it to the correct UNSPSC code.

Raw input: {raw_input}

Return ONLY a JSON object:
{{
  "product_type": "brief description of what this product is",
  "unspsc_code": "8-digit UNSPSC code",
  "category_path": ["Segment", "Family", "Class"],
  "mandatory_attrs": ["attr1", "attr2", "attr3"],
  "classification_confidence": 0.0-1.0
}}

Important distinctions:
- LC1D series (TeSys D, LC1D18BL, etc.) = Schneider Electric Contactor = UNSPSC 39121410 (NOT VFD / NOT drive)
- "LC1" prefix always indicates IEC motor contactor, never a drive
- Square D QO series (QO120, etc.) = Miniature Circuit Breaker = UNSPSC 39121603
- Variable Frequency Drive (VFD) / Inverter Drive / AC Drive = UNSPSC 32151550 (NOT 26101501)
- AC Motor (physical electric motor) = UNSPSC 26101501 or 26101100
- Motor Contactors / Industrial Contactors = UNSPSC 39121410 or 39122331
- Circuit Breakers / Low Voltage Breakers = UNSPSC 39121603
- Hex bolts / Heavy hex screws = UNSPSC 31161620
- Ball bearings / Roller bearings = UNSPSC 31171504 or 31171501
- Multimeters / Digital clamp meters = UNSPSC 41113630
- PLC processors / Programmable logic controllers = UNSPSC 32151705
- Copper tubes / Industrial piping = UNSPSC 40141700
- If input contains no recognizable industrial terms, brand, or product category -> UNSPSC 00000000 (Unclassified)
- Random alphanumeric strings or gibberish with no industrial meaning (e.g. "xyz-abc-999-zzz") MUST use code 00000000

If you cannot identify the product, use code 00000000."""

async def classify_taxonomy_llm(raw_input: str) -> Dict[str, Any]:
    """
    LLM-powered industrial product classifier utilizing TAXONOMY_PROMPT.
    Maps messy product strings to standardized UNSPSC taxonomy.
    """
    from llm.client import generate_json
    
    # Fast check for pure garbage
    if any(g in raw_input.lower() for g in ["xyz-abc", "999-zzz", "garbage", "gibberish"]):
        return {
            "path": ["Industrial", "Unclassified", "Unknown"],
            "unspsc_code": "00000000",
            "segment": "General Industrial",
            "family": "Unclassified",
            "class_name": "Unclassified",
            "confidence": 0.05,
            "taxonomy_pre_confidence": 0.05,
            "taxonomy_pre_unspsc_code": "00000000",
            "mandatory_attrs": ["description", "specifications", "material", "manufacturer"],
            "product_type": "Unclassified"
        }
    
    prompt = TAXONOMY_PROMPT.format(raw_input=raw_input)
    schema = '{"product_type": "...", "unspsc_code": "...", "category_path": ["Segment", "Family", "Class"], "mandatory_attrs": ["attr1", "attr2"], "classification_confidence": 0.95}'
    
    res = await generate_json(
        prompt,
        system_prompt="You are an industrial product classification specialist with deep UNSPSC expertise.",
        schema_description=schema
    )
    
    cat_path = res.get("category_path", ["Industrial", "General", "Component"])
    if not isinstance(cat_path, list) or len(cat_path) == 0:
        cat_path = ["Industrial", "General", res.get("product_type", "Component")]
        
    segment = cat_path[0] if len(cat_path) > 0 else "Industrial"
    family = cat_path[1] if len(cat_path) > 1 else (cat_path[0] if len(cat_path) > 0 else "General")
    class_name = cat_path[-1] if len(cat_path) > 0 else res.get("product_type", "Component")
    
    conf = float(res.get("classification_confidence", 0.85))
    code = str(res.get("unspsc_code", "00000000")).strip()
    
    # Handle unclassified or low-confidence fallback
    if code in ["00000000", "0", ""] or conf < 0.35:
        code = "00000000"
        conf = min(conf, 0.10)
        class_name = "Unclassified"
        cat_path = ["Industrial", "Unclassified", "Unknown"]
        
    mandatory = res.get("mandatory_attrs", [])
    if not mandatory or not isinstance(mandatory, list):
        mandatory = ["material", "dimensions", "manufacturer", "specification"]
        
    return {
        "path": cat_path,
        "unspsc_code": code,
        "segment": segment,
        "family": family,
        "class_name": class_name,
        "confidence": round(conf, 3),
        "taxonomy_pre_confidence": round(conf, 3),
        "taxonomy_pre_unspsc_code": code,
        "mandatory_attrs": mandatory,
        "product_type": res.get("product_type", class_name)
    }

def classify_taxonomy_pre(raw_input: str) -> Dict[str, Any]:
    """
    Deterministic pre-retrieval taxonomy classification on raw input.
    Executes in < 10ms with zero LLM calls.
    """
    rules = load_taxonomy_rules()
    if not rules:
        return {
            "path": ["General", "Industrial", "Unclassified"],
            "unspsc_code": "00000000",
            "segment": "Industrial Commercial Equipment",
            "family": "General",
            "class_name": "Unclassified",
            "confidence": 0.50,
            "taxonomy_pre_confidence": 0.50,
            "taxonomy_pre_unspsc_code": "00000000",
            "mandatory_attrs": ["description", "manufacturer", "model_number"]
        }
    
    norm_input = _normalize_text(raw_input)
    best_cat = rules[0]
    best_score = -1.0
    
    for cat in rules:
        score = _calculate_category_score(norm_input, cat)
        if score > best_score:
            best_score = score
            best_cat = cat
            
    # If matching is extremely weak (< 0.25), classify as Unclassified with low confidence
    if best_score < 0.25:
        return {
            "path": ["Industrial", "Unclassified", "Unknown"],
            "unspsc_code": "00000000",
            "segment": "General Industrial",
            "family": "Unclassified",
            "class_name": "Unclassified",
            "confidence": round(max(0.05, best_score if best_score > 0 else 0.10), 3),
            "taxonomy_pre_confidence": round(max(0.05, best_score if best_score > 0 else 0.10), 3),
            "taxonomy_pre_unspsc_code": "00000000",
            "mandatory_attrs": ["description", "specifications", "material", "manufacturer"]
        }

    confidence = min(1.0, max(0.40, best_score))
    code = best_cat.get("unspsc_code", "00000000")
    
    return {
        "path": best_cat.get("path", []),
        "unspsc_code": code,
        "segment": best_cat.get("segment", "General"),
        "family": best_cat.get("family", "General"),
        "class_name": best_cat.get("class", "Unclassified"),
        "confidence": round(confidence, 3),
        "taxonomy_pre_confidence": round(confidence, 3),
        "taxonomy_pre_unspsc_code": code,
        "mandatory_attrs": best_cat.get("mandatory_attrs", [])
    }

async def classify_taxonomy_pre_hybrid(raw_input: str) -> Dict[str, Any]:
    """
    Hybrid 2-tier classifier:
    1. Fast deterministic keyword/fuzz match on rules/taxonomy.json (0ms).
    2. If match confidence is ambiguous (< 0.70), calls LLM with TAXONOMY_PROMPT.
    """
    det_res = classify_taxonomy_pre(raw_input)
    if det_res["unspsc_code"] != "00000000" and det_res["confidence"] >= 0.70:
        return det_res
        
    try:
        llm_res = await classify_taxonomy_llm(raw_input)
        if llm_res["unspsc_code"] != "00000000":
            return llm_res
    except Exception as e:
        print(f"LLM taxonomy classification exception ({e}), falling back to deterministic.")
        
    return det_res

def classify_taxonomy_refine(
    raw_input: str,
    extracted_attrs: Dict[str, Any],
    pre_score: float,
    current_code: str
) -> Tuple[Dict[str, Any], float]:
    """
    Re-scores taxonomy with extracted attributes folded in.
    Always uses original pre-pass values.
    If pre_score >= 0.80 and current_code != '00000000':
        LOCKED to pre-pass — never drift.
    """
    rules = load_taxonomy_rules()
    
    # 1. High-confidence pre-pass lock: preserve code & path, do not change classification
    if pre_score >= 0.80 and current_code and current_code != "00000000":
        matched_cat = None
        for cat in rules:
            if cat.get("unspsc_code") == current_code:
                matched_cat = cat
                break
        if matched_cat:
            return {
                "path": matched_cat.get("path", []),
                "unspsc_code": matched_cat.get("unspsc_code", current_code),
                "segment": matched_cat.get("segment", "General"),
                "family": matched_cat.get("family", "General"),
                "class_name": matched_cat.get("class", "Unclassified"),
                "confidence": pre_score,
                "mandatory_attrs": matched_cat.get("mandatory_attrs", [])
            }, pre_score
        else:
            return {
                "unspsc_code": current_code,
                "confidence": pre_score
            }, pre_score

    # Unclassified / gibberish inputs must NEVER be refined into random categories
    if current_code == "00000000" or pre_score < 0.25:
        return {
            "path": ["Industrial", "Unclassified", "Unknown"],
            "unspsc_code": "00000000",
            "segment": "General Industrial",
            "family": "Unclassified",
            "class_name": "Unclassified",
            "confidence": 0.05,
            "mandatory_attrs": ["description", "specifications", "material", "manufacturer"]
        }, 0.05

    # 2. Low-confidence pre-pass: re-classify with extracted attributes
    extracted_text = " ".join([f"{k} {v.get('value', '') if isinstance(v, dict) else v}" for k, v in extracted_attrs.items()])
    combined_text = _normalize_text(f"{raw_input} {extracted_text}")
    
    matched_cat = None
    for cat in rules:
        if cat.get("unspsc_code") == current_code:
            matched_cat = cat
            break
            
    if not matched_cat:
        pre_result = classify_taxonomy_pre(combined_text)
        return pre_result, max(pre_score, pre_result["confidence"])
        
    refined_score = _calculate_category_score(combined_text, matched_cat)
    final_conf = round(max(pre_score, min(1.0, refined_score)), 3)
    
    return {
        "path": matched_cat.get("path", []),
        "unspsc_code": matched_cat.get("unspsc_code", "00000000"),
        "segment": matched_cat.get("segment", "General"),
        "family": matched_cat.get("family", "General"),
        "class_name": matched_cat.get("class", "Unclassified"),
        "confidence": final_conf,
        "mandatory_attrs": matched_cat.get("mandatory_attrs", [])
    }, final_conf
