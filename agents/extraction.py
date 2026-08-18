import json
import logging
from typing import Dict, Any, List
from llm.client import generate_json

logger = logging.getLogger("pimpulse.extraction")

FEW_SHOT_EXAMPLES = """
Example 1:
Input: "chv-blt-1/2-ss-316"
Category: Bolts (Mandatory: material, thread_size, length, grade)
Context: "Grade 316 Marine Grade Stainless Steel Heavy Hex Bolt. Thread size: 1/2-13 UNC coarse machine thread. Standard nominal length: 2.5 inches."
Output:
{
  "attributes": {
    "material": {"value": "Stainless Steel 316", "unit": null, "source_snippet": "Grade 316 Marine Grade Stainless Steel"},
    "thread_size": {"value": "1/2-13 UNC", "unit": "in", "source_snippet": "1/2-13 UNC coarse machine thread"},
    "length": {"value": "2.5", "unit": "in", "source_snippet": "nominal length: 2.5 inches"},
    "grade": {"value": "SS 316", "unit": null, "source_snippet": "Grade 316"}
  },
  "standardized_title": "1/2\"-13 UNC x 2.5\" Stainless Steel 316 Heavy Hex Bolt",
  "marketing_description": "Corrosion-resistant 316 marine-grade stainless steel heavy hex bolt designed for extreme environments.",
  "feature_bullets": [
    "Grade 316 marine austenitic alloy construction",
    "1/2-13 UNC coarse pitch threads for heavy duty clamping",
    "Precision manufactured for industrial and offshore applications"
  ]
}

Example 2:
Input: "Siemens 3RT2015-1BB41"
Category: Motor contactors (Mandatory: coil_voltage, power_rating, poles, contact_configuration)
Context: "SIRIUS power contactor, 3-pole, AC-3, 4 kW / 400 V, 1 NO auxiliary contact, 24 V DC control supply voltage, screw terminal, size S00."
Output:
{
  "attributes": {
    "coil_voltage": {"value": "24V DC", "unit": "V", "source_snippet": "24 V DC control supply voltage"},
    "power_rating": {"value": "4 kW", "unit": "kW", "source_snippet": "4 kW / 400 V"},
    "poles": {"value": "3", "unit": "P", "source_snippet": "3-pole"},
    "contact_configuration": {"value": "1 NO", "unit": null, "source_snippet": "1 NO auxiliary contact"}
  },
  "standardized_title": "Siemens SIRIUS 3RT2015-1BB41 3-Pole 4kW Contactor (24V DC)",
  "marketing_description": "Compact Siemens SIRIUS 3RT2015 contactor for electric motor control with 24VDC coil and integrated 1 NO auxiliary.",
  "feature_bullets": [
    "4 kW power rating at 400V (AC-3)",
    "24 V DC control supply voltage",
    "3-Pole power contact with 1 NO auxiliary contact",
    "Finger-safe IP20 screw terminals"
  ]
}
"""

async def extract_attributes_targeted(
    raw_input: str,
    category_class: str,
    mandatory_attrs: List[str],
    graded_chunks: List[Dict[str, Any]],
    current_extracted: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Few-shot prompted attribute extraction specifically targeting mandatory category attributes.
    Returns: {attributes, standardized_title, marketing_description, feature_bullets, provenance}
    """
    mandatory_lower = [str(attr).lower().strip() for attr in mandatory_attrs] if mandatory_attrs else []
    targeting_hint = f"MANDATORY ATTRIBUTES TO EXTRACT (use lowercase keys): {mandatory_lower}\n" if mandatory_lower else ""
    context_text = "\n\n".join([f"Source ({c.get('url', 'local')}):\n{c.get('content', '')}" for c in graded_chunks])

    prompt = (
        f"You are an industrial PIM data extraction specialist.\n"
        f"Extract structured, verified product attributes from the context text below for this product.\n\n"
        f"Target Product Input: '{raw_input}'\n"
        f"Classified Category: '{category_class}'\n"
        f"{targeting_hint}\n"
        f"Reference Examples:\n{FEW_SHOT_EXAMPLES}\n\n"
        f"Context from technical documents:\n"
        f"{context_text}\n\n"
        f"Instructions:\n"
        f"1. Extract each mandatory attribute and any key technical properties found in the text.\n"
        f"2. Use lowercase attribute keys (e.g. 'material', 'voltage', 'current_rating', 'poles').\n"
        f"3. Include the exact verbatim source snippet in 'source_snippet'.\n"
        f"4. Generate a clean, standardized title, marketing description, and 3-4 feature bullets.\n"
        f"5. Output strict JSON with keys: 'attributes', 'standardized_title', 'marketing_description', 'feature_bullets'."
    )
    
    schema = '{"attributes": {"attr_name": {"value": "...", "unit": "...", "source_snippet": "..."}}, "standardized_title": "...", "marketing_description": "...", "feature_bullets": ["..."]}'
    try:
        res = await generate_json(prompt, system_prompt="You are a precise industrial catalog enrichment engine.", schema_description=schema)
    except Exception as e:
        logger.error(f"[extraction] LLM call failed for '{raw_input}': {e}")
        res = {}
    
    # Log if LLM returned an error or empty attributes
    if res.get("error"):
        logger.error(f"[extraction] LLM returned error for '{raw_input}': {res.get('error')}. Raw: {str(res.get('raw', ''))[:200]}")
    
    raw_attrs = res.get("attributes", {})
    if not raw_attrs:
        logger.error(f"[extraction] LLM returned EMPTY attributes for '{raw_input}'. Full response keys: {list(res.keys())}. Response preview: {str(res)[:300]}")
    clean_attrs = {}
    provenance = {}
    
    # Associate each extracted attribute with a provenance URL from chunks
    default_url = graded_chunks[0].get("url") if graded_chunks else "https://catalog.unilogcorp.com/spec"
    
    for k, v in raw_attrs.items():
        k_clean = str(k).lower().strip().replace("-", "_")
        if isinstance(v, dict):
            val = str(v.get("value", ""))
            unit = v.get("unit")
            snip = v.get("source_snippet", "")
        else:
            val = str(v)
            unit = None
            snip = val
            
        clean_attrs[k_clean] = {
            "value": val,
            "unit": unit,
            "source": "extracted",
            "source_snippet": snip,
            "confidence": 0.95
        }
        
        # Find which chunk has snippet or value
        matched_url = default_url
        for c in graded_chunks:
            if val.lower() in c.get("content", "").lower() or (snip and snip.lower() in c.get("content", "").lower()):
                matched_url = c.get("url") or default_url
                break
        provenance[k_clean] = matched_url

    # Check for brand / specific MPN to detect ambiguous generic queries
    INVALID_VALS = {"", "none", "null", "n/a", "unknown", "unspecified", "generic", "-", "--"}
    has_brand = False
    has_mpn = False
    
    for k, v in clean_attrs.items():
        k_lower = k.lower()
        val = str(v.get("value", "")).strip().lower()
        if val and val not in INVALID_VALS:
            if any(b_key in k_lower for b_key in ["brand", "manufacturer", "oem", "make"]):
                has_brand = True
            if any(m_key in k_lower for m_key in ["mpn", "part_number", "model", "catalog_number", "item_number"]):
                has_mpn = True

    # Also inspect raw input for specific known brands or part-code patterns
    KNOWN_BRANDS = {
        "siemens", "schneider", "abb", "eaton", "skf", "fag", "nsk", "timken",
        "festo", "smc", "omron", "sick", "ifm", "mcmaster", "fastenal",
        "fluke", "swagelok", "danfoss", "square d", "allen bradley", "rockwell"
    }
    raw_lower = raw_input.lower()
    for b in KNOWN_BRANDS:
        if b in raw_lower:
            has_brand = True
            break
            
    import re
    # Hyphenated structured MPNs or model codes
    if re.search(r"[a-z0-9]+-[a-z0-9]+-[a-z0-9]+", raw_lower) or re.search(r"\b[0-9]{4,}[a-z0-9-]*\b", raw_lower):
        has_mpn = True
    if re.search(r"\b(87v|6205|3rt|lc1d|qo120|fc-051|ss-4-vcr)\b", raw_lower):
        has_mpn = True

    ambiguity_flag = not (has_brand or has_mpn)

    return {
        "extracted_attrs": clean_attrs,
        "standardized_title": res.get("standardized_title", raw_input),
        "marketing_description": res.get("marketing_description", f"Industrial product specification for {raw_input}"),
        "feature_bullets": res.get("feature_bullets", ["High quality industrial component", "Manufactured to OEM standards"]),
        "provenance": provenance,
        "ambiguity_flag": ambiguity_flag
    }
