"""
PIMpulse AI — Delta-Aware Idempotent Re-Enrichment Engine
Computes cryptographic content fingerprints, eliminates redundant LLM calls on second runs,
and tracks breaking taxonomy/UOM changes in an append-only Change Impact Ledger.
"""

import hashlib
import json
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("pimpulse.delta")

DELTA_SCHEMA_VERSION = "1.0.0"

def compute_sku_fingerprint(
    raw_row: Dict[str, Any],
    schema_version: str = DELTA_SCHEMA_VERSION,
    model_id: str = "claude-opus-5"
) -> str:
    """
    Computes a deterministic SHA-256 fingerprint for a raw SKU input payload.
    Identical payloads across runs produce identical hashes.
    """
    canonical_payload = {
        "mfr_part_num": str(raw_row.get("Mfg_Part_Num", "")).strip().lower(),
        "part_desc": str(raw_row.get("Part_Desc", "")).strip().lower(),
        "part_manuf": str(raw_row.get("Part_Manuf", "")).strip().lower(),
        "schema_version": schema_version,
        "model_id": model_id
    }
    serialized = json.dumps(canonical_payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def evaluate_delta(
    raw_row: Dict[str, Any],
    previous_cache: Dict[str, Dict[str, Any]],
    current_model_id: str = "claude-opus-5"
) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Evaluates an incoming SKU against the historical cache store.
    Returns:
      (status, fingerprint, cached_result_if_unchanged)
      status in: {"UNCHANGED", "SOURCE_CHANGED", "SCHEMA_CHANGED", "NEW"}
    """
    mpn = str(raw_row.get("Mfg_Part_Num", "")).strip()
    fingerprint = compute_sku_fingerprint(raw_row, model_id=current_model_id)

    if mpn not in previous_cache:
        return "NEW", fingerprint, None

    cached_entry = previous_cache[mpn]
    cached_hash = cached_entry.get("fingerprint", "")
    cached_schema = cached_entry.get("schema_version", "")

    if fingerprint == cached_hash:
        logger.info(f"Fingerprint HIT for SKU '{mpn}'. Skipping LLM enrichment ($0 spend).")
        return "UNCHANGED", fingerprint, cached_entry.get("enriched_output")

    if cached_schema != DELTA_SCHEMA_VERSION:
        return "SCHEMA_CHANGED", fingerprint, None

    return "SOURCE_CHANGED", fingerprint, None

def generate_change_ledger(
    old_output: Dict[str, Any],
    new_output: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a structured diff ledger between prior enrichment and new enrichment.
    Flags breaking UNSPSC or UOM shifts for human sign-off.
    """
    changes = []
    has_breaking_change = False

    all_keys = set(old_output.keys()) | set(new_output.keys())
    for key in sorted(all_keys):
        old_val = old_output.get(key)
        new_val = new_output.get(key)

        if old_val != new_val:
            is_breaking = key in ("UNSPSC", "ATTRIBUTE_UOM 1", "ATTRIBUTE_UOM 2", "ATTRIBUTE_UOM 3")
            if is_breaking:
                has_breaking_change = True

            changes.append({
                "field": key,
                "previous": old_val,
                "updated": new_val,
                "is_breaking": is_breaking,
                "status": "BREAKING_CHANGE_HOLD" if is_breaking else "MODIFIED"
            })

    return {
        "sku": new_output.get("MANUFACTURER_PART_NUMBER", ""),
        "total_changes": len(changes),
        "has_breaking_change": has_breaking_change,
        "action": "HOLD_FOR_APPROVAL" if has_breaking_change else "AUTOPUBLISH",
        "diff_ledger": changes
    }
