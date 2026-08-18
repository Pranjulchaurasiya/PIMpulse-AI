import pytest
import asyncio
import re
from typing import Dict, Any

from agents.taxonomy import classify_taxonomy_pre, classify_taxonomy_refine, classify_taxonomy_pre_hybrid
from agents.unilog_rules import (
    resolve_manufacturer_brand,
    parse_abrasive_dimensions,
    format_invoice_desc,
    format_mobile_desc,
    format_short_desc,
    match_lov_value,
    format_fraction_value,
    APPROVED_MATERIAL_LOV,
    APPROVED_APPLICATION_LOV
)
from agents.confidence import calculate_mathematical_confidence
from agents.grounding import check_attributes_grounding, is_value_grounded
from cache import SemanticCache
from graph import pimpulse_pipeline
from state import ProductState
from config import settings

@pytest.fixture(autouse=True)
def setup_test_env():
    prev = settings.PROVIDER
    settings.PROVIDER = "mock"
    yield
    settings.PROVIDER = prev

# =========================================================================
# 1. ADVERSARIAL & MESSY INPUT TAXONOMY TESTS
# =========================================================================

def test_adversarial_gibberish_classification():
    """Gibberish and non-industrial strings must classify as Unclassified with 00000000 code and low confidence."""
    gibberish_inputs = [
        "xyz-abc-999-zzz",
        "random non-industrial text blablabla",
        "1234567890!@#$%",
        "completely unknown weird gadget 9999"
    ]
    for inp in gibberish_inputs:
        res = classify_taxonomy_pre(inp)
        assert res["unspsc_code"] == "00000000"
        assert res["confidence"] <= 0.35
        assert res["class_name"] == "Unclassified"

def test_messy_industrial_inputs_taxonomy():
    """Messy strings with delimiters and punctuation must map to correct UNSPSC classes."""
    test_cases = [
        ("!!! 4-1/2 IN. X .045 IN. X 7/8 IN. TYPE 27 METAL CUT OFF WHEEL #49-94-0107 (PKG OF 25) !!!", "31191506"),
        ("chv-blt-1/2-ss-316", "31161620"),
        ("Siemens 3RT2015-1BB41 24VDC SIRIUS", "39121410"),
        ("Square D QO120 1P 20A 120V Circuit Breaker", "39121603"),
        ("SKF 6205-2RSH/C3 Deep Groove Ball Bearing", "31171504"),
        ("Fluke 87V True RMS Industrial Multimeter", "41113630"),
        ("Swagelok SS-4-VCR-1-4 Female Nut 1/4 in", "40141700"),
        ("3M 775L Stikit Film Disc P150 Cubitron II", "31191500"),
        ("Diablo 4-1/2 in x 1/8 in x 7/8 in Grinding Wheel Type 27", "31191600")
    ]
    for raw, expected_code in test_cases:
        res = classify_taxonomy_pre(raw)
        assert res["unspsc_code"] == expected_code, f"Failed for '{raw}': got {res['unspsc_code']}, expected {expected_code}"
        assert res["confidence"] >= 0.40

# =========================================================================
# 2. STRICT MDM DESCRIPTION INVARIANT TESTS
# =========================================================================

def test_invoice_desc_token_boundary_invariants():
    """INVOICE_DESC must strictly be <= 40 chars, ALL CAPS, without slicing words."""
    test_specs = [
        ("MILW", "49-94-0107", {"diameter": "4-1/2", "thickness": ".045", "arbor_size": "7/8"}, "Milwaukee 4-1/2 In x .045 in x 7/8 in Performance+ Metal Cut-Off Wheel"),
        ("DIAB", "DCB518ASTS06G", {"width": "1/2", "length": "18"}, "Diablo 1/2 in x 18 in Sanding Belt"),
        ("3M", "7100075678", {"grit": "150"}, "3M 775L Stikit Film Disc P150 Cubitron II 50 Disc/Box"),
        ("NORT", "66252830591", {"diameter": "14", "thickness": "7/64", "arbor_size": "1"}, "Norton Gemini 14 in x 7/64 in x 1 in Metal Cutting Cut-Off Wheel"),
        ("PFRD", "63124", {"diameter": "9", "thickness": "1/8", "arbor_size": "7/8"}, "PFERD Performance Line SG-ELASTIC Masonry Cut-Off Wheel")
    ]
    for mfr_code, mpn, dims, desc in test_specs:
        inv = format_invoice_desc(mfr_code, mpn, dims, desc)
        assert len(inv) <= 40, f"INVOICE_DESC exceeded 40 chars: '{inv}' (len={len(inv)})"
        assert inv == inv.upper(), f"INVOICE_DESC is not ALL CAPS: '{inv}'"
        # Must not end in trailing punctuation
        assert not inv.endswith(("-", "/", "X", ",")), f"INVOICE_DESC ended abruptly: '{inv}'"

def test_mobile_desc_length_range_invariants():
    """MOBILE_DESC must strictly be between 60 and 80 chars inclusive."""
    test_cases = [
        ("Milwaukee Electric Tool Corporation", "Milwaukee®", "49-94-0107", "Metal Cut-Off Disc", {"diameter": "4-1/2", "thickness": ".045", "arbor_size": "7/8"}, "Performance+"),
        ("Freud America, Inc.", "Diablo®", "DCB518ASTS06G", "Sanding Belt", {"width": "1/2", "length": "18"}, ""),
        ("3M Company", "3M™", "7100075678", "Stikit™ Film Disc", {"grit": "150"}, "Cubitron™ II"),
        ("Saint-Gobain Abrasives, Inc.", "Norton®", "66252830591", "Cut-Off Wheel", {"diameter": "14", "thickness": "7/64", "arbor_size": "1"}, "Gemini"),
        ("Siemens Industry, Inc.", "Siemens®", "3RT2015-1BB41", "Motor Contactor", {}, "SIRIUS"),
        ("SKF USA Inc.", "SKF®", "6205-2RSH", "Deep Groove Ball Bearing", {}, "")
    ]
    for mfr, brand, mpn, itype, dims, series in test_cases:
        mob = format_mobile_desc(mfr, brand, mpn, itype, dims, series)
        assert 60 <= len(mob) <= 80, f"MOBILE_DESC '{mob}' has len={len(mob)}, expected [60, 80]"

# =========================================================================
# 3. BRAND & MFR CANONICAL RESOLUTION TESTS
# =========================================================================

def test_brand_canonical_resolution():
    """Test resolution of various brand name formats according to Unilog master data standards."""
    cases = [
        ("Milwaukee Accessory (4031)", "49-94-0107 4-1/2 IN CUT-OFF", "Milwaukee Tool", "Milwaukee", "MILW"),
        ("Freud America (DIAB)", "DCB518 Sanding Belt", "Freud America, Inc.", "Diablo", "DIAB"),
        ("Jam Industrial / 3M", "3M 775L Cubitron Disc", "3M Company", "3M", "3M"),
        ("Mirka Abrasives (MIRK)", "Abranet 3x4 in Mesh", "Mirka Abrasives, Inc.", "Mirka", "MIRK"),
        ("Saint-Gobain Abrasives", "Norton Gemini Cut-Off", "Saint-Gobain Abrasives, Inc.", "Norton", "NORT"),
        ("Weiler Abrasives (WEIL)", "Weiler Tiger Cut-Off Disc", "Weiler Abrasives Group", "Weiler", "WEIL")
    ]
    for part_mfr, desc, exp_mfr, exp_brand, exp_code in cases:
        res = resolve_manufacturer_brand(part_mfr, desc)
        assert res["mfr_name"] == exp_mfr
        assert res["brand_name"] == exp_brand
        assert res["mfr_code"] == exp_code

# =========================================================================
# 4. MATHEMATICAL CONFIDENCE & AMBIGUITY TESTS
# =========================================================================

def test_confidence_math_invariants():
    """Test ambiguity penalty, cold-start redistribution, and calibration."""
    mandatory = ["material", "thread_size", "length", "grade"]
    extracted = {
        "material": {"value": "Stainless Steel 316"},
        "thread_size": {"value": "1/2-13 UNC"},
        "length": {"value": "2.5 in"},
        "grade": {"value": "316"}
    }
    
    # 1. Clean product with full grounding
    conf_clean = calculate_mathematical_confidence(
        mandatory_attrs=mandatory,
        extracted_attrs=extracted,
        grounding_ratio=1.0,
        retrieval_agreement_rate=0.0,
        vector_store_empty=True,
        vision_agreement_rate=1.0,
        taxonomy_confidence=1.0,
        vision_conflicts=[],
        ambiguity_flag=False
    )
    assert conf_clean["confidence_pct"] == 100.0
    assert conf_clean["coverage"] == 1.0
    assert conf_clean["ambiguity_penalty"] == 0.0

    # 2. Ambiguous generic product (missing Brand/MPN) -> 25% penalty
    conf_ambig = calculate_mathematical_confidence(
        mandatory_attrs=mandatory,
        extracted_attrs=extracted,
        grounding_ratio=1.0,
        retrieval_agreement_rate=0.0,
        vector_store_empty=True,
        vision_agreement_rate=1.0,
        taxonomy_confidence=1.0,
        vision_conflicts=[],
        ambiguity_flag=True
    )
    assert conf_ambig["ambiguity_penalty"] == 0.25
    assert 50.0 <= conf_ambig["confidence_pct"] <= 75.0

    # 3. Unclassified gibberish input -> must be capped <= 20%
    conf_gibberish = calculate_mathematical_confidence(
        mandatory_attrs=mandatory,
        extracted_attrs={},
        grounding_ratio=0.0,
        retrieval_agreement_rate=0.0,
        vector_store_empty=True,
        vision_agreement_rate=1.0,
        taxonomy_confidence=0.05,
        vision_conflicts=[],
        ambiguity_flag=True
    )
    assert conf_gibberish["confidence_pct"] <= 20.0

# =========================================================================
# 5. END-TO-END PIPELINE WITH PRESET BENCHMARKS
# =========================================================================

@pytest.mark.asyncio
async def test_full_pipeline_all_presets():
    """Verify all 4 core presets complete through the full LangGraph pipeline."""
    presets = [
        ("chv-blt-1/2-ss-316", "31161620", "Bolts"),
        ("Siemens 3RT2015-1BB41", "39121410", "Motor contactors"),
        ("3P 20A CB", "39121603", "Circuit breakers"),
        ("SKF 6205-2RSH", "31171504", "Ball bearings")
    ]
    for raw_inp, exp_unspsc, exp_class in presets:
        st: ProductState = {
            "raw_input": raw_inp,
            "image_path": None,
            "retry_count": 0,
            "agent_logs": []
        }
        res = await pimpulse_pipeline.ainvoke(st)
        profile = res.get("final_profile")
        assert profile is not None, f"Pipeline returned None profile for {raw_inp}"
        assert profile["taxonomy"]["code"] == exp_unspsc, f"Wrong UNSPSC for {raw_inp}: got {profile['taxonomy']['code']}"
        assert len(profile["attributes"]) > 0, f"Zero attributes extracted for {raw_inp}"
        assert profile["confidence"]["confidence_pct"] > 0
        assert len(res.get("agent_logs", [])) >= 8
