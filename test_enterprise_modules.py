"""
PIMpulse AI — Enterprise Winning Modules Test Suite
Validates Delta Engine, Source Authority, Cryptographic Audit Ledger,
Semantic Truncator, Attribute Confidence Tiers, and Data Contract Schema.
"""

import pytest
import yaml
import os
from agents.delta_engine import compute_sku_fingerprint, evaluate_delta, generate_change_ledger
from agents.authority import classify_source_authority, normalize_marketing_units, resolve_attribute_conflict
from agents.confidence import classify_attribute_confidence_tier
from agents.audit_trail import create_audit_record, verify_chain_integrity, GENESIS_HASH
from agents.semantic_truncator import semantic_truncate_invoice_desc

# ==============================================================================
# TEST 1: Delta-Aware Idempotent Re-Enrichment & Breaking Change Ledger
# ==============================================================================

def test_delta_fingerprint_and_idempotency():
    raw_row = {
        "Mfg_Part_Num": "49-94-0107",
        "Part_Desc": "4-1/2 IN. METAL CUT-OFF WHEEL",
        "Part_Manuf": "Milwaukee Tool"
    }

    fp1 = compute_sku_fingerprint(raw_row)
    fp2 = compute_sku_fingerprint(raw_row)
    assert fp1 == fp2, "Fingerprint calculation must be deterministic"

    cache_store = {
        "49-94-0107": {
            "fingerprint": fp1,
            "schema_version": "1.0.0",
            "enriched_output": {"MANUFACTURER_NAME": "Milwaukee Tool", "UNSPSC": "31191600"}
        }
    }

    status, fp, cached_out = evaluate_delta(raw_row, cache_store)
    assert status == "UNCHANGED", "Identical input payload must hit cache as UNCHANGED ($0 spend)"
    assert cached_out["UNSPSC"] == "31191600"

def test_delta_change_ledger_breaking_hold():
    old_output = {"UNSPSC": "31191600", "ATTRIBUTE_VALUE 1": "4.5", "ATTRIBUTE_UOM 1": "in"}
    new_output = {"UNSPSC": "27112800", "ATTRIBUTE_VALUE 1": "4.5", "ATTRIBUTE_UOM 1": "in"}

    ledger = generate_change_ledger(old_output, new_output)
    assert ledger["has_breaking_change"] is True
    assert ledger["action"] == "HOLD_FOR_APPROVAL"
    assert ledger["diff_ledger"][0]["field"] == "UNSPSC"

# ==============================================================================
# TEST 2: Source Authority Ranking & Marketing Unit Trap Normalization
# ==============================================================================

def test_source_authority_ranking():
    tier, score = classify_source_authority("https://www.milwaukeetool.com/datasheet/49-94-0107.pdf", mfr_domain="milwaukeetool.com")
    assert tier == "oem_pdf" and score == 1.00

    tier, score = classify_source_authority("https://www.grainger.com/product/MILWAUKEE-Cut-Off-Wheel", mfr_domain="milwaukeetool.com")
    assert tier == "distributor" and score == 0.70

def test_marketing_unit_normalization():
    assert normalize_marketing_units("20V MAX Lithium Battery") == "18 V Lithium Battery"
    assert normalize_marketing_units("5inch Abrasive Disc") == "5 in Abrasive Disc"

def test_conflict_resolution_by_authority():
    candidates = [
        {"value": "20V MAX", "source_url": "https://www.amazon.com/dp/B00123"},
        {"value": "18 V", "source_url": "https://www.milwaukeetool.com/Products/49-94-0107"}
    ]
    winner_val, winner_score, rationale = resolve_attribute_conflict(candidates, mfr_domain="milwaukeetool.com")
    assert winner_val == "18 V"
    assert winner_score == 0.95

# ==============================================================================
# TEST 3: Cryptographic Audit Ledger & Chain Integrity
# ==============================================================================

def test_audit_ledger_cryptographic_verification():
    records = []
    
    # Record 1
    r1 = create_audit_record("49-94-0107", "UNSPSC", "31191600", prev_record_hash=GENESIS_HASH)
    records.append(r1)

    # Record 2
    r2 = create_audit_record("49-94-0107", "BRAND_NAME", "Milwaukee", prev_record_hash=r1["record_hash"])
    records.append(r2)

    # Verify untampered chain
    valid, msg = verify_chain_integrity(records)
    assert valid is True
    assert "100% untampered" in msg

    # Tamper with record 1
    records[0]["new_value"] = "99999999"
    valid, msg = verify_chain_integrity(records)
    assert valid is False, "Chain verification must detect record tampering"

# ==============================================================================
# TEST 4: Semantic Token-Importance Truncator
# ==============================================================================

def test_semantic_truncator():
    raw_desc = "GENUINE SPECIAL PERFORMANCE MILWAUKEE 4-1/2 IN. X .045 IN. X 7/8 IN. METAL CUT-OFF WHEEL"
    truncated = semantic_truncate_invoice_desc(raw_desc, brand_name="MILWAUKEE", mpn="49-94-0107", max_length=40)

    assert len(truncated) <= 40, f"Length {len(truncated)} exceeds 40: '{truncated}'"
    assert truncated == truncated.upper()
    assert "MILWAUKEE" in truncated
    assert "SPECIAL" not in truncated, "Noise stop words should be stripped first"

# ==============================================================================
# TEST 5: Attribute Confidence Tiers (A/B/C/D)
# ==============================================================================

def test_confidence_tiers():
    tier_a = classify_attribute_confidence_tier("Material", "Aluminum Oxide", is_verbatim_grounded=True, source_authority_tier="oem_web")
    assert tier_a["tier"] == "A" and tier_a["action"] == "AUTOPUBLISH"

    tier_c = classify_attribute_confidence_tier("Material", "Aluminum Oxide", is_verbatim_grounded=True, source_authority_tier="distributor", has_conflict=True)
    assert tier_c["tier"] == "C" and tier_c["action"] == "REVIEW_REQUIRED"

    tier_d = classify_attribute_confidence_tier("Material", "", is_verbatim_grounded=False, source_authority_tier="unverified")
    assert tier_d["tier"] == "D" and tier_d["action"] == "REJECTED_NULL"

# ==============================================================================
# TEST 6: Versioned Data Contract YAML Validation
# ==============================================================================

def test_data_contract_yaml_schema():
    contract_path = os.path.join("rules", "unilog_contract_v1.yaml")
    assert os.path.exists(contract_path), f"Data contract missing at {contract_path}"

    with open(contract_path, "r", encoding="utf-8") as f:
        contract = yaml.safe_load(f)

    assert contract["name"] == "Unilog Master Catalog Data Contract"
    assert "INVOICE_DESC" in contract["columns"]
    assert contract["columns"]["INVOICE_DESC"]["max_length"] == 40
    assert contract["columns"]["UNSPSC"]["exact_length"] == 8
