import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Tuple

def _sliding_windows(text: str, window_len: int, step: int = 1):
    text_len = len(text)
    if window_len <= 0 or text_len <= 0:
        return
    if window_len >= text_len:
        yield text
        return
    for i in range(0, text_len - window_len + 1, step):
        yield text[i:i + window_len]

INVALID_GROUND_VALS = {"", "none", "null", "n/a", "unknown", "none/not specified", "unspecified"}

def is_value_grounded(value: str, context: str, threshold: float = 0.60) -> Tuple[bool, str]:
    """
    Deterministic grounding verification:
    1. Exact case-insensitive substring match
    2. Token-level normalization match (handles unit formatting like '24V DC' vs '24 VDC')
    3. Sliding-window fuzzy SequenceMatcher
    """
    if not value or not context:
        return False, ""

    v_clean = value.strip().lower()
    if v_clean in INVALID_GROUND_VALS:
        return False, ""
    c_clean = context.lower()

    # 1. Exact substring
    if v_clean in c_clean:
        return True, value

    # 2. Space/hyphen normalized
    v_compact = re.sub(r"[\s\-_/]", "", v_clean)
    c_compact = re.sub(r"[\s\-_/]", "", c_clean)
    if v_compact in c_compact and len(v_compact) >= 2:
        return True, value

    # 3. Sliding window fuzzy match
    target_len = len(v_clean)
    best_ratio = 0.0
    best_snippet = ""

    for window in _sliding_windows(c_clean, target_len, step=2):
        ratio = SequenceMatcher(None, v_clean, window).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_snippet = window
        if ratio >= threshold:
            return True, best_snippet

    return False, best_snippet

def check_attributes_grounding(
    extracted_attrs: Dict[str, Any],
    retrieved_chunks: List[Dict[str, Any]],
    threshold: float = 0.60,
    min_grounding_ratio: float = 0.70
) -> Tuple[bool, float, Dict[str, bool]]:
    """
    Evaluates grounding for all extracted attributes against the combined retrieved text.
    Returns: (grounding_ok, grounding_ratio, grounded_flags)
    """
    if not extracted_attrs:
        return False, 0.0, {}

    combined_context = " ".join([c.get("content", "") + " " + c.get("title", "") for c in retrieved_chunks])
    
    normalized_extracted = {str(k).lower().strip(): v for k, v in extracted_attrs.items()}
    grounded_flags = {}
    grounded_count = 0
    total_attrs = len(normalized_extracted)

    for attr_name, attr_data in normalized_extracted.items():
        if isinstance(attr_data, dict):
            val = str(attr_data.get("value", ""))
            snippet_ctx = str(attr_data.get("source_snippet", ""))
        else:
            val = str(attr_data)
            snippet_ctx = ""

        target_context = f"{snippet_ctx} {combined_context}".strip()
        is_grd, snippet = is_value_grounded(val, target_context, threshold=threshold)
        grounded_flags[attr_name] = is_grd
        if is_grd:
            grounded_count += 1

    ratio = round(grounded_count / max(total_attrs, 1), 3)
    grounding_ok = ratio >= min_grounding_ratio

    return grounding_ok, ratio, grounded_flags
