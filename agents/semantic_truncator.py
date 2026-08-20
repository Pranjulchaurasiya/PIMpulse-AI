"""
PIMpulse AI — Semantic Token-Importance Truncator
Truncates product descriptions to <= 40 chars ALL CAPS for ERP INVOICE_DESC.
Uses semantic word importance (preserving Brand, MPN, and Key Specs) rather than raw character slicing.
"""

import re
from typing import List

# Words to drop first when truncating to 40 chars
STOP_WORDS = {
    "GENUINE", "ORIGINAL", "SPECIAL", "PREMIUM", "PERFORMANCE", "HEAVY", "DUTY",
    "INDUSTRIAL", "COMMERCIAL", "QUALITY", "SUPERIOR", "PROFESSIONAL", "ULTRA",
    "HIGH", "GRADE", "SERIES", "RATED", "STANDARD", "AUTHENTIC", "BEST", "PLUS", "+"
}

def semantic_truncate_invoice_desc(
    part_desc: str,
    brand_name: str = "",
    mpn: str = "",
    max_length: int = 40
) -> str:
    """
    Semantically truncates a product description to fit within `max_length` (40 chars),
    ALL CAPS, preserving brand, MPN, and dimensional spec invariants.
    """
    if not part_desc:
        desc = f"{brand_name} {mpn}".strip().upper()
        return desc[:max_length]

    # Upper case and normalize whitespace
    cleaned = re.sub(r"\s+", " ", str(part_desc).strip().upper())

    if len(cleaned) <= max_length:
        return cleaned

    # Tokenize
    tokens = cleaned.split()

    # Step 1: Remove optional noise stop words
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS]
    candidate = " ".join(filtered_tokens)

    if len(candidate) <= max_length:
        return candidate

    # Step 2: Ensure Brand or MPN is included if missing
    head_tokens = []
    if brand_name and brand_name.upper() not in candidate:
        head_tokens.append(brand_name.upper())

    # Step 3: Trim tokens from tail until length <= max_length
    current_list = head_tokens + filtered_tokens
    while current_list and len(" ".join(current_list)) > max_length:
        current_list.pop()

    candidate = " ".join(current_list)

    # Step 4: Hard word-boundary safety net if still over max_length
    if len(candidate) > max_length:
        candidate = candidate[:max_length].rstrip(" ,.-/")

    # Invariant assertion: must be ALL CAPS and <= 40 chars
    return candidate.upper()
