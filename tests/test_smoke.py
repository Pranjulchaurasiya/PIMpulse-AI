import pytest
import asyncio
from agents.taxonomy import classify_taxonomy_pre, classify_taxonomy_refine
from agents.hyde import expand_query_hyde
from retrieval.hybrid import reciprocal_rank_fusion
from agents.grounding import check_attributes_grounding, is_value_grounded
from agents.confidence import calculate_mathematical_confidence, build_final_product_profile
from cache import SemanticCache
from graph import pimpulse_pipeline
from state import ProductState, ProductProfile
from config import settings

@pytest.fixture(autouse=True)
def setup_test_env():
    prev = settings.PROVIDER
    settings.PROVIDER = "mock"
    yield
    settings.PROVIDER = prev

def test_taxonomy_pre_and_rapid_fuzz():
    # Test keyword matching for bolt
    res_bolt = classify_taxonomy_pre("chv-blt-1/2-ss-316")
    assert res_bolt["class_name"] == "Bolts"
    assert res_bolt["unspsc_code"] == "31161620"
    assert "material" in res_bolt["mandatory_attrs"]
    assert res_bolt["confidence"] >= 0.50

    # Test circuit breaker
    res_cb = classify_taxonomy_pre("3P 20A CB")
    assert res_cb["class_name"] == "Circuit breakers"
    assert res_cb["unspsc_code"] == "39121603"
    assert "voltage" in res_cb["mandatory_attrs"]

    # Test refine monotonic non-decreasing score
    refined, final_conf = classify_taxonomy_refine(
        "chv-blt-1/2-ss-316",
        {"material": "Stainless Steel 316", "thread_size": "1/2-13 UNC"},
        res_bolt["confidence"],
        res_bolt["unspsc_code"]
    )
    assert final_conf >= res_bolt["confidence"]

@pytest.mark.asyncio
async def test_hyde_expansion():
    # Short query (<40 chars) should trigger expansion
    exp_q, hypo, is_exp = await expand_query_hyde("3RT2015-1BB41", "Motor contactors")
    assert is_exp is True
    assert len(exp_q) > len("3RT2015-1BB41")
    assert hypo != ""

    # Long query should NOT expand
    long_input = "Siemens 3RT2015-1BB41 SIRIUS 3-Pole 4kW AC-3 24VDC Power Contactor"
    exp_long, hypo_long, is_exp_long = await expand_query_hyde(long_input, "Motor contactors")
    assert is_exp_long is False

def test_reciprocal_rank_fusion():
    list_a = [{"id": "doc1", "title": "A"}, {"id": "doc2", "title": "B"}]
    list_b = [{"id": "doc2", "title": "B"}, {"id": "doc3", "title": "C"}]
    
    fused, agreement = reciprocal_rank_fusion([list_a, list_b], k=60, top_n=5)
    assert len(fused) == 3
    # doc2 appeared in both lists, so its RRF score must be highest
    assert fused[0]["id"] == "doc2"
    assert fused[0]["multi_source"] is True
    assert agreement > 0.0

def test_grounding_substring_and_fuzzy():
    context = "The Siemens SIRIUS 3RT2015-1BB41 features a 24V DC operating coil voltage and 4 kW power at 400V."
    
    # Exact substring
    grounded_1, snip_1 = is_value_grounded("24V DC", context)
    assert grounded_1 is True

    # Unit formatting variation (24 VDC vs 24V DC)
    grounded_2, snip_2 = is_value_grounded("24 VDC", context)
    assert grounded_2 is True

    # Check non-existent hallucinated value
    grounded_3, _ = is_value_grounded("480V 3-Phase Special Edition", context)
    assert grounded_3 is False

    # Check batch
    extracted = {
        "coil_voltage": {"value": "24V DC"},
        "power_rating": {"value": "4 kW"}
    }
    chunks = [{"content": context}]
    ok, ratio, flags = check_attributes_grounding(extracted, chunks)
    assert ok is True
    assert ratio == 1.0
    assert flags["coil_voltage"] is True
    assert flags["power_rating"] is True

def test_mathematical_confidence_cold_start():
    # Test Cold Start (vector_store_empty = True)
    mandatory = ["voltage", "current_rating", "poles", "breaking_capacity"]
    extracted = {
        "voltage": "415V AC",
        "current_rating": "20A",
        "poles": "3P",
        "breaking_capacity": "10 kA"
    }
    
    conf = calculate_mathematical_confidence(
        mandatory_attrs=mandatory,
        extracted_attrs=extracted,
        grounding_ratio=1.0,
        retrieval_agreement_rate=0.0,
        vector_store_empty=True,  # Cold store
        vision_agreement_rate=1.0,
        taxonomy_confidence=0.85,
        vision_conflicts=[]
    )
    
    assert conf["retrieval_agreement_excluded"] is True
    assert conf["coverage"] == 1.0
    assert conf["grounding_ratio"] == 1.0
    assert conf["confidence_pct"] > 90.0
    # Check redistributed weights sum to 1.0
    weights_sum = sum(conf["weights_used"].values())
    assert round(weights_sum, 2) == 1.00

def test_semantic_cache():
    cache = SemanticCache(similarity_threshold=0.96)
    profile = {"standardized_title": "Test Profile", "confidence": {"confidence_pct": 95.0}}
    
    # Store
    cache.set("chv-blt-1/2-ss-316", profile)
    
    # Exact lookup
    hit_exact, htype_1, lat_1 = cache.get("chv-blt-1/2-ss-316")
    assert hit_exact is not None
    assert htype_1 == "EXACT_HIT"
    assert lat_1 < 50.0  # sub-50ms

    # Miss lookup
    miss, htype_2, lat_2 = cache.get("completely-different-motor-part-xyz")
    assert miss is None
    assert htype_2 == "MISS"

def test_ambiguity_flag_and_penalty():
    mandatory = ["voltage", "current_rating", "poles", "breaking_capacity"]
    extracted = {
        "voltage": "480V",
        "current_rating": "20A",
        "poles": "3P",
        "breaking_capacity": "10 kA"
    }
    
    # 1. Clean MPN (ambiguity_flag = False)
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
    assert conf_clean["ambiguity_penalty"] == 0.0

    # 2. Ambiguous query (ambiguity_flag = True) -> 25% penalty & generic taxonomy cap
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
    assert 50.0 <= conf_ambig["confidence_pct"] <= 70.0  # In the requested 50-70% range

@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    initial_state: ProductState = {
        "raw_input": "chv-blt-1/2-ss-316",
        "image_path": None,
        "retry_count": 0,
        "agent_logs": []
    }
    
    final_state = await pimpulse_pipeline.ainvoke(initial_state)
    profile_dict = final_state.get("final_profile")
    
    assert profile_dict is not None
    assert profile_dict["standardized_title"] != ""
    assert profile_dict["taxonomy"]["code"] == "31161620"
    assert "material" in profile_dict["attributes"]
    assert profile_dict["confidence"]["confidence_pct"] > 0
    assert len(final_state.get("agent_logs", [])) >= 8
