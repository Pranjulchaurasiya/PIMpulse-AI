"""
PIMpulse AI — Cryptographic Hash-Chained Audit Ledger
Generates immutable, append-only records of data enrichment actions.
Provides mathematical integrity verification to prove zero record tampering.
"""

import hashlib
import json
import time
from typing import Dict, Any, List, Tuple

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

def create_audit_record(
    sku: str,
    attribute_name: str,
    new_value: Any,
    actor: str = "agent:unilog-pipeline-v2.5",
    source_url: str = "",
    confidence_tier: str = "A",
    prev_record_hash: str = GENESIS_HASH
) -> Dict[str, Any]:
    """
    Creates an immutable, hash-chained audit record for a single attribute change.
    """
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    record_payload = {
        "sku": str(sku),
        "attribute_name": str(attribute_name),
        "new_value": str(new_value),
        "actor": actor,
        "source_url": source_url,
        "confidence_tier": confidence_tier,
        "timestamp": timestamp,
        "prev_hash": prev_record_hash
    }
    
    serialized = json.dumps(record_payload, sort_keys=True)
    record_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    
    record_payload["record_hash"] = record_hash
    return record_payload

def verify_chain_integrity(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validates the cryptographic chain integrity of a list of audit records.
    Returns (is_valid, status_message).
    """
    if not records:
        return True, "Audit log is empty."

    expected_prev = GENESIS_HASH
    for idx, rec in enumerate(records, 1):
        if rec.get("prev_hash") != expected_prev:
            return False, f"Broken chain link at index {idx} (SKU {rec.get('sku')}): expected prev_hash '{expected_prev}', got '{rec.get('prev_hash')}'"

        # Re-compute current hash
        payload_copy = {k: v for k, v in rec.items() if k != "record_hash"}
        serialized = json.dumps(payload_copy, sort_keys=True)
        computed_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        if computed_hash != rec.get("record_hash"):
            return False, f"Tampered record at index {idx} (SKU {rec.get('sku')}): computed hash '{computed_hash}' != stored '{rec.get('record_hash')}'"

        expected_prev = rec.get("record_hash")

    return True, f"Chain integrity verified: {len(records)} records 100% untampered."
