from typing import Dict, List, Optional, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# Pydantic V2 Schemas for Verification & API Output
# -------------------------------------------------------------

class AttributeValue(BaseModel):
    value: str
    unit: Optional[str] = None
    source: str = "extracted"  # "extracted" | "web_verified" | "vision_confirmed" | "cached"
    grounded: bool = False
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_snippet: Optional[str] = None

class UNSPSCClassification(BaseModel):
    code: str = Field(description="8-digit standard UNSPSC Code")
    segment: str
    family: str
    class_name: str = Field(description="Commodity/Class designation")
    path: List[str]

class ConfidenceBreakdown(BaseModel):
    coverage: float
    grounding_ratio: float
    retrieval_agreement: float
    retrieval_agreement_excluded: bool
    vision_match: float
    taxonomy_confidence: float
    conflict_penalty: float
    ambiguity_penalty: float = 0.0
    ambiguity_flag: bool = False
    confidence_pct: float
    weights_used: Dict[str, float]

class ProductProfile(BaseModel):
    raw_input: str
    standardized_title: str
    taxonomy: UNSPSCClassification
    attributes: Dict[str, AttributeValue]
    marketing_description: str
    feature_bullets: List[str]
    vision_agreement_rate: Optional[float] = None
    vision_conflicts: List[str] = Field(default_factory=list)
    ambiguity_flag: bool = False
    confidence: ConfidenceBreakdown
    evaluator_decision: str  # "accept" | "retry" | "escalate"
    provenance: Dict[str, str] = Field(default_factory=dict)  # attr_name -> source_url/id
    cached: bool = False
    latency_ms: Optional[float] = None

# -------------------------------------------------------------
# LangGraph Reducers & State Definition
# -------------------------------------------------------------

def merge_dicts(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Merge reducer: new keys add, conflicting keys take newer value."""
    if not left:
        return right or {}
    if not right:
        return left
    merged = dict(left)
    merged.update(right)
    return merged

def append_logs(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Log reducer: appends log entries chronologically."""
    if not left:
        return right or []
    if not right:
        return left
    return left + right

def replace_chunks(left: List[Dict[str, Any]], right: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chunk reducer: replace chunks on new search iteration."""
    if right is not None:
        return right
    return left or []

class ProductState(TypedDict, total=False):
    raw_input: str
    image_path: Optional[str]
    search_query: str
    is_cached: bool
    
    # Taxonomy
    taxonomy_path: List[str]
    unspsc_code: str
    unspsc_segment: str
    unspsc_family: str
    unspsc_class: str
    taxonomy_confidence: float
    taxonomy_pre_confidence: float
    taxonomy_pre_unspsc_code: str
    mandatory_attrs: List[str]
    
    # HyDE
    hyde_hypothesis: Optional[str]
    
    # Retrieval & Grading
    retrieved_chunks: Annotated[List[Dict[str, Any]], replace_chunks]
    vector_store_empty: bool
    graded_chunks: List[Dict[str, Any]]
    
    # Extraction & Grounding
    extracted_attrs: Annotated[Dict[str, Any], merge_dicts]
    grounding_ok: bool
    grounding_ratio: float
    grounded_flags: Dict[str, bool]
    ambiguity_flag: bool
    
    # Vision
    vision_raw_attrs: Dict[str, Any]
    vision_agreement_rate: float
    vision_conflicts: List[str]
    
    # Audit & Retry Loop
    retry_count: int
    missing_mandatory_attrs: List[str]
    evaluator_decision: str  # "accept" | "retry" | "ask_user"
    audit_notes: str
    
    # Confidence & Final Output
    confidence_breakdown: Dict[str, Any]
    final_profile: Optional[Dict[str, Any]]
    standardized_title: str
    marketing_description: str
    feature_bullets: List[str]
    provenance: Dict[str, str]
    
    # Telemetry stream logs
    agent_logs: Annotated[List[Dict[str, Any]], append_logs]
