"""
Official UniHack 2026 Evaluator Test Suite (Simulating the Judges' 200 Hidden Items Evaluation Script)
Tests against the strict criteria set by Ramachandra Raje Urs (VP, Content Services, Unilog).
"""

import pytest
import asyncio
from agents.unilog_rules import (
    format_invoice_desc_hardened,
    format_mobile_desc_hardened,
    format_short_desc,
    match_lov_value,
    standardize_uom,
    APPROVED_MATERIAL_LOV,
    CANONICAL_MFR_BRAND
)
from agents.unilog_pipeline import enrich_unilog_row, UNILOG_DELIVERY_COLUMNS
from data.master_catalog_1000 import get_master_industrial_catalog

# ==============================================================================
# TEST 1: The 3 Canonical Evaluator Stress Cases
# ==============================================================================

@pytest.mark.asyncio
async def test_evaluator_stress_case_1_milwaukee_clean_pass():
    """
    Stress Case 1: MILW-49-94-0107-DISC
    - Manufacturer: Normalized to 'Milwaukee Tool'
    - Brand: Normalized to 'Milwaukee'
    - UNSPSC: 31191600 (Abrasives / Cut-off Wheels)
    - INVOICE_DESC: <= 40 chars, ALL CAPS
    - MOBILE_DESC: 60 - 80 chars
    """
    raw_row = {
        "Mfg_Part_Num": "49-94-0107",
        "Part_Desc": "4-1/2 IN. X .045 IN. X 7/8 IN. METAL CUT-OFF WHEEL (4031)",
        "Part_Manuf": "Milwaukee Accessory (4031)"
    }
    
    enriched = await enrich_unilog_row(raw_row)
    
    assert enriched["MANUFACTURER_NAME"] == "Milwaukee Tool"
    assert enriched["BRAND_NAME"] == "Milwaukee"
    assert enriched["MANUFACTURER_PART_NUMBER"] == "49-94-0107"
    assert enriched["UNSPSC"] == "31191600"
    
    # Description Invariants
    inv = enriched["INVOICE_DESC"]
    mob = enriched["MOBILE_DESC"]
    assert len(inv) <= 40, f"INVOICE_DESC length {len(inv)} exceeds 40: '{inv}'"
    assert inv == inv.upper(), f"INVOICE_DESC not ALL CAPS: '{inv}'"
    assert 60 <= len(mob) <= 80, f"MOBILE_DESC length {len(mob)} outside [60, 80]: '{mob}'"
    assert enriched["SOURCE_URL"].startswith("https://www.milwaukeetool.com")

@pytest.mark.asyncio
async def test_evaluator_stress_case_2_mirka_lov_uom_trap():
    """
    Stress Case 2: MIRKA 23-612-180
    - Material LOV: Must select from approved vocabulary ('Aluminum Oxide')
    - UOM Standard: Separate space ('5 in', NOT '5inch' or '5in')
    """
    raw_row = {
        "Mfg_Part_Num": "23-612-180",
        "Part_Desc": "5inch Abranet Grip Mesh Disc 180 Grit Alum Oxide",
        "Part_Manuf": "Mirka Abrasives (MIRK)"
    }
    
    enriched = await enrich_unilog_row(raw_row)
    
    assert enriched["BRAND_NAME"] == "Mirka"
    assert enriched["ATTRIBUTE_LABEL 1"] == "Diameter"
    assert enriched["ATTRIBUTE_VALUE 1"] == "5"
    assert enriched["ATTRIBUTE_UOM 1"] == "in"
    assert enriched["ATTRIBUTE_LABEL 2"] == "Grit"
    assert enriched["ATTRIBUTE_VALUE 2"] == "180"
    assert enriched["ATTRIBUTE_LABEL 3"] == "Material"
    assert enriched["ATTRIBUTE_VALUE 3"] == "Aluminum Oxide"
    
    # UOM separation in mobile description
    mob = enriched["MOBILE_DESC"]
    assert "5 in" in mob or "5 IN" in mob.upper()
    assert "5inch" not in mob.lower()
    assert 60 <= len(mob) <= 80

@pytest.mark.asyncio
async def test_evaluator_stress_case_3_dead_site_graceful_degradation():
    """
    Stress Case 3: UNCATEGORIZED_ABRASIVE_WHEEL
    - When manufacturer website is unavailable / dead, system must gracefully degrade
      to unclassified / clean fallback without hallucinating fabricated values.
    """
    raw_row = {
        "Mfg_Part_Num": "UNKNOWN-ABR-9999",
        "Part_Desc": "Nonexistent Custom Mystery Grinding Disc XYZ999",
        "Part_Manuf": "Nonexistent Industrial Corp"
    }
    
    enriched = await enrich_unilog_row(raw_row)
    
    # Must still produce compliant descriptions
    assert len(enriched["INVOICE_DESC"]) <= 40
    assert 60 <= len(enriched["MOBILE_DESC"]) <= 80
    assert enriched["SOURCE_URL"] != ""
    # Should not crash and should produce standard columns
    assert "ATTRIBUTE_LABEL 1" in enriched
    assert "UNSPSC" in enriched

# ==============================================================================
# TEST 2: 200-Item Hidden Evaluator Simulation Suite
# ==============================================================================

@pytest.mark.asyncio
async def test_hidden_200_item_evaluator_simulation():
    """
    Simulates the judges' automated grading script running against 200 hidden,
    diverse industrial items drawn from across all 25 industrial categories.
    Verifies 100% compliance on all Unilog delivery columns and description bounds.
    """
    master_items = get_master_industrial_catalog()
    
    # Generate 200 distinct test cases
    test_cases = []
    for i in range(200):
        item = master_items[i % len(master_items)]
        test_cases.append({
            "Mfg_Part_Num": f"{item['mpn']}-T{i+1}",
            "Part_Desc": f"{item['title']} - Industrial Test Spec Item #{i+1}",
            "Part_Manuf": item['mfr_name'],
            "E1_Brand": item['brand_name']
        })
        
    sem = asyncio.Semaphore(25)
    async def process_item(r):
        async with sem:
            return await enrich_unilog_row(r)
            
    results = await asyncio.gather(*[process_item(r) for r in test_cases])
    
    assert len(results) == 200
    
    # Audit 100% of the 200 items against strict rules
    for idx, r in enumerate(results, 1):
        inv = r["INVOICE_DESC"]
        mob = r["MOBILE_DESC"]
        
        # 1. Column presence
        assert "MANUFACTURER_NAME" in r
        assert "BRAND_NAME" in r
        assert "SOURCE_URL" in r
        assert "UNSPSC" in r
        assert "ATTRIBUTE_LABEL 1" in r
        assert "ATTRIBUTE_VALUE 1" in r
        assert "ATTRIBUTE_UOM 1" in r
        
        # 2. Hard Invariant 1: INVOICE_DESC <= 40 chars & ALL CAPS
        assert len(inv) <= 40, f"Row {idx} INVOICE_DESC ({len(inv)} chars) exceeded 40: '{inv}'"
        assert inv == inv.upper(), f"Row {idx} INVOICE_DESC is not ALL CAPS: '{inv}'"
        
        # 3. Hard Invariant 2: MOBILE_DESC in [60, 80] chars
        assert 60 <= len(mob) <= 80, f"Row {idx} MOBILE_DESC ({len(mob)} chars) out of range [60, 80]: '{mob}'"
        
        # 4. UNSPSC must be 8 digits
        assert len(r["UNSPSC"]) == 8 and r["UNSPSC"].isdigit(), f"Row {idx} UNSPSC '{r['UNSPSC']}' is not 8 digits"
        
    print("\n✅ Successfully validated all 200 hidden simulation test items with 100% compliance!")
