import logging
from typing import Dict, Any, List, Optional, Tuple
from llm.client import analyze_image

logger = logging.getLogger("pimpulse.vision")

async def vision_describe(image_path: Optional[str]) -> Dict[str, Any]:
    """
    Parallel vision branch: independently extracts visual attributes from product image
    without waiting for text extraction.
    """
    if not image_path:
        return {
            "image_present": False,
            "vision_raw_attrs": {},
            "description": "No product image supplied."
        }

    prompt = (
        "Analyze this industrial product image.\n"
        "Identify and return key visual properties:\n"
        "1. Dominant Material (e.g. Stainless Steel, Brass, Thermoplastic, Aluminum)\n"
        "2. Dominant Color (e.g. Metallic Silver, Black, Grey, Blue)\n"
        "3. Physical Form / Shape (e.g. Hex Head Bolt, Modular DIN Rail, Flanged Cylinder)\n"
        "4. Any visible label markings, ratings, or part numbers."
    )
    
    res = await analyze_image(image_path, prompt)
    return {
        "image_present": True,
        "vision_raw_attrs": res.get("visual_attributes", {}),
        "description": res.get("description", "")
    }

def reconcile_vision_with_text(
    vision_raw_attrs: Dict[str, Any],
    extracted_attrs: Dict[str, Any],
    image_present: bool
) -> Tuple[float, List[str]]:
    """
    Reconciles vision properties against extracted text values.
    Returns: (vision_agreement_rate, list_of_conflicts)
    """
    if not image_present or not vision_raw_attrs:
        # No image supplied -> neutral agreement (1.0) with 0 conflicts
        return 1.0, []

    conflicts = []
    comparisons = 0
    matches = 0

    # Material check
    v_mat = str(vision_raw_attrs.get("material", "")).lower()
    text_mat = ""
    for k, v in extracted_attrs.items():
        if "material" in k.lower():
            text_mat = str(v.get("value", "") if isinstance(v, dict) else v).lower()
            break

    if v_mat and text_mat:
        comparisons += 1
        # Check token intersection
        v_tokens = set(v_mat.replace("/", " ").replace("-", " ").split())
        t_tokens = set(text_mat.replace("/", " ").replace("-", " ").split())
        if v_tokens.intersection(t_tokens) or "steel" in v_mat and "ss" in text_mat or "316" in text_mat:
            matches += 1
        else:
            conflicts.append(f"Material discrepancy: Image indicates '{v_mat}' while extracted text specifies '{text_mat}'.")

    # Color check
    v_col = str(vision_raw_attrs.get("color", "")).lower()
    text_col = ""
    for k, v in extracted_attrs.items():
        if "color" in k.lower():
            text_col = str(v.get("value", "") if isinstance(v, dict) else v).lower()
            break

    if v_col and text_col:
        comparisons += 1
        v_tokens = set(v_col.split())
        t_tokens = set(text_col.split())
        if v_tokens.intersection(t_tokens):
            matches += 1
        else:
            conflicts.append(f"Color mismatch: Image shows '{v_col}' whereas text indicates '{text_col}'.")

    if comparisons == 0:
        agreement_rate = 1.0
    else:
        agreement_rate = round(matches / comparisons, 3)

    return agreement_rate, conflicts
