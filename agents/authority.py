"""
PIMpulse AI — Source Authority & Conflict Resolution Engine
Ranks retrieved data sources by domain trust authority, resolves candidate conflicts,
and normalizes industrial marketing unit traps (e.g. 18V MAX / 20V Peak -> 18 V).
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("pimpulse.authority")

AUTHORITY_HIERARCHY = {
    "oem_pdf": 1.00,
    "oem_web": 0.95,
    "distributor": 0.70,  # Grainger, Fastenal, MSC
    "marketplace": 0.35,  # Amazon, eBay
    "unverified": 0.00
}

DISTRIBUTOR_DOMAINS = ["grainger.com", "fastenal.com", "mscdirect.com", "mcmaster.com"]
MARKETPLACE_DOMAINS = ["amazon.com", "ebay.com", "walmart.com", "aliexpress.com"]

def classify_source_authority(url: str, mfr_domain: str = "") -> Tuple[str, float]:
    """
    Classifies a URL into a source authority tier and assigns a numeric score.
    """
    if not url:
        return "unverified", 0.00

    url_lower = url.lower()
    
    # PDF Spec Sheet check
    if url_lower.endswith(".pdf") or "/datasheet/" in url_lower or "/specsheet/" in url_lower:
        if mfr_domain and mfr_domain.lower() in url_lower:
            return "oem_pdf", AUTHORITY_HIERARCHY["oem_pdf"]
        return "distributor", AUTHORITY_HIERARCHY["distributor"]

    # OEM Web Page check
    if mfr_domain and mfr_domain.lower() in url_lower:
        return "oem_web", AUTHORITY_HIERARCHY["oem_web"]

    # Distributor check
    if any(d in url_lower for d in DISTRIBUTOR_DOMAINS):
        return "distributor", AUTHORITY_HIERARCHY["distributor"]

    # Marketplace check
    if any(m in url_lower for m in MARKETPLACE_DOMAINS):
        return "marketplace", AUTHORITY_HIERARCHY["marketplace"]

    return "distributor", AUTHORITY_HIERARCHY["distributor"]

VOLTAGE_CLEANER = {
    "18V MAX": "18 V",
    "20V PEAK": "18 V",
    "20V MAX": "18 V",
    "12V MAX": "10.8 V",
    "10.8V": "10.8 V",
    "60V MAX": "54 V"
}

def normalize_marketing_units(value_str: str) -> str:
    """
    Normalizes industrial marketing platform traps.
    e.g., '18V MAX' / '20V Peak' -> '18 V', '12V MAX' -> '10.8 V', '5inch' -> '5 in'
    """
    if not value_str:
        return value_str

    val = str(value_str).strip()

    # Marketing voltage platform traps
    for mkt, norm in VOLTAGE_CLEANER.items():
        if re.search(rf"(?i)\b{re.escape(mkt)}\b", val):
            val = re.sub(rf"(?i)\b{re.escape(mkt)}\b", norm, val)

    val = re.sub(r"(?i)\b20\s*v\s*(max|peak)\b", "18 V", val)
    val = re.sub(r"(?i)\b18\s*v\s*(max|nominal)\b", "18 V", val)
    val = re.sub(r"(?i)\b12\s*v\s*max\b", "10.8 V", val)

    # Separate unit spaces (e.g. 5inch -> 5 in, 10mm -> 10 mm)
    val = re.sub(r"(?i)(\d+)\s*(inch|in\b)", r"\1 in", val)
    val = re.sub(r"(?i)(\d+)\s*(mm|millimeter)", r"\1 mm", val)

    return val

def resolve_attribute_conflict(
    candidates: List[Dict[str, Any]],
    mfr_domain: str = ""
) -> Tuple[str, float, str]:
    """
    Resolves conflicting candidate values for an attribute based on source authority.
    Each candidate item: {"value": str, "source_url": str}
    Returns:
      (winning_value, winning_authority_score, resolution_rationale)
    """
    if not candidates:
        return "", 0.00, "No candidates provided"

    scored_candidates = []
    for cand in candidates:
        val = normalize_marketing_units(cand.get("value", ""))
        url = cand.get("source_url", "")
        tier_name, score = classify_source_authority(url, mfr_domain=mfr_domain)
        scored_candidates.append({
            "value": val,
            "url": url,
            "tier": tier_name,
            "score": score
        })

    # Sort by authority score descending
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    winner = scored_candidates[0]

    rationale = f"Accepted '{winner['value']}' from {winner['tier']} authority ({winner['url']}) with score {winner['score']:.2f}"
    return winner["value"], winner["score"], rationale
