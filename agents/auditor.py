import logging
from typing import Dict, Any, List, Tuple
from config import settings

logger = logging.getLogger("pimpulse.auditor")

# Canonical attribute aliases for standard industrial attributes
ATTRIBUTE_ALIASES = {
    "material": ["material", "body_material", "construction_material", "alloy", "steel_type"],
    "thread_size": ["thread_size", "thread", "threads_per_inch", "pitch", "diameter", "size", "thread_type", "thread_pitch"],
    "length": ["length", "overall_length", "nominal_length", "depth", "tube_length"],
    "grade": ["grade", "material_grade", "alloy_grade", "material", "standard"],
    "voltage": ["voltage", "supply_voltage", "rated_voltage", "operating_voltage", "coil_voltage", "ac_voltage"],
    "current_rating": ["current_rating", "current", "rated_current", "amperage", "amps", "amp_rating"],
    "poles": ["poles", "number_of_poles", "pole_count", "phase", "configuration"],
    "breaking_capacity": ["breaking_capacity", "interrupt_rating", "interrupting_capacity", "aic", "ka_rating", "short_circuit_current", "breaking_capacity_ka"],
    "coil_voltage": ["coil_voltage", "control_voltage", "voltage", "supply_voltage"],
    "power_rating": ["power_rating", "rated_power", "motor_power", "kw", "hp", "horsepower"],
    "contact_configuration": ["contact_configuration", "auxiliary_contacts", "contacts", "contact_type", "poles"],
    "bore_diameter": ["bore_diameter", "bore_size", "inside_diameter", "inner_diameter", "bore", "id"],
    "outer_diameter": ["outer_diameter", "outside_diameter", "od", "diameter", "size"],
    "width": ["width", "thickness", "height", "depth"],
    "seal_type": ["seal_type", "closure", "shield_type", "seals", "enclosure"],
    "dynamic_load": ["dynamic_load", "load_rating", "basic_dynamic_load", "dynamic_load_rating", "load_capacity"],
    "fitting_type": ["fitting_type", "type", "connection_type", "fitting", "end_connection", "tube_type", "form"],
    "pressure_rating": ["pressure_rating", "pressure", "working_pressure", "max_pressure", "pressure_class", "wall_thickness", "length"],
    "input_voltage": ["input_voltage", "voltage", "supply_voltage", "line_voltage"],
    "output_frequency": ["output_frequency", "frequency", "speed_range", "frequency_range"],
    "phase": ["phase", "number_of_phases", "input_phase", "poles"],
    "speed_rpm": ["speed_rpm", "rpm", "speed", "rated_speed", "synchronous_speed"],
    "frame_size": ["frame_size", "frame", "mounting", "nema_frame", "iec_frame"],
    "efficiency_class": ["efficiency_class", "efficiency", "energy_efficiency", "ie_class"],
    "measurement_type": ["measurement_type", "type", "measurement_functions", "function", "parameters"],
    "display_counts": ["display_counts", "display", "counts", "resolution", "digits"],
    "safety_rating": ["safety_rating", "cat_rating", "safety_category", "cat_iv", "cat_iii"],
    "accuracy": ["accuracy", "dc_accuracy", "basic_accuracy", "precision"]
}

# Optional fallbacks if primary defining attributes are already present
OPTIONAL_IF_PRESENT = {
    "grade": ["material"],
    "breaking_capacity": ["voltage", "current_rating"],
    "fitting_type": ["material", "outer_diameter"],
    "pressure_rating": ["material", "outer_diameter"],
    "dynamic_load": ["bore_diameter", "outer_diameter"],
    "efficiency_class": ["power_rating", "speed_rpm"],
    "seal_type": ["bore_diameter", "outer_diameter"],
    "accuracy": ["measurement_type", "display_counts"]
}

def audit_enrichment_state(
    extracted_attrs: Dict[str, Any],
    mandatory_attrs: List[str],
    grounding_ok: bool,
    grounding_ratio: float,
    vision_agreement_rate: float,
    retry_count: int,
    raw_input: str,
    ambiguity_flag: bool = False,
    unspsc_code: str = ""
) -> Dict[str, Any]:
    """
    Deterministic quality and consistency audit.
    Checks:
    1. Grounding ratio >= 0.70 (0.50 on retries)
    2. Mandatory attributes presence (with alias & fallback resolution)
    3. Vision agreement rate >= 0.50
    4. Ambiguity flag (missing brand and MPN)
    5. UNSPSC code validity (00000000 -> ask_user)
    
    Returns decision: 'accept' | 'retry' | 'ask_user'
    """
    if unspsc_code == "00000000":
        return {
            "evaluator_decision": "ask_user",
            "missing_mandatory_attrs": mandatory_attrs,
            "new_search_query": raw_input,
            "audit_notes": "Unclassified product: no recognizable industrial category or standard specifications found. Escalating to human reviewer."
        }
    missing_mandatory = []
    extracted_lower = {str(k).lower().strip().replace("-", "_").replace(" ", "_"): v for k, v in extracted_attrs.items()}
    INVALID_VALS = {"", "none", "null", "n/a", "unknown", "unspecified", "generic", "-", "--"}
    
    def _is_attr_present(key: str) -> bool:
        k_norm = str(key).lower().strip().replace("-", "_").replace(" ", "_")
        aliases = ATTRIBUTE_ALIASES.get(k_norm, [k_norm])
        for alias in aliases:
            for ex_k, val in extracted_lower.items():
                if alias == ex_k or alias in ex_k or ex_k in alias:
                    v_str = str(val.get("value", "") if isinstance(val, dict) else val).strip().lower()
                    if v_str and v_str not in INVALID_VALS:
                        return True
        return False

    for mandatory_key in mandatory_attrs:
        m_norm = str(mandatory_key).lower().strip().replace("-", "_").replace(" ", "_")
        found = _is_attr_present(m_norm)
        
        # Fallback check: if optional when primary attributes are present
        if not found and m_norm in OPTIONAL_IF_PRESENT:
            deps = OPTIONAL_IF_PRESENT[m_norm]
            if all(_is_attr_present(dep) for dep in deps):
                found = True
                
        if not found:
            missing_mandatory.append(mandatory_key)

    effective_grounding_threshold = 0.50 if retry_count >= 1 else settings.GROUNDING_THRESHOLD
    is_grounded = grounding_ok or grounding_ratio >= effective_grounding_threshold
    has_mandatory = len(missing_mandatory) == 0
    vision_ok = vision_agreement_rate >= 0.50

    audit_notes = []
    if not is_grounded:
        audit_notes.append(f"Grounding ratio {grounding_ratio:.2f} below threshold {effective_grounding_threshold:.2f}.")
    if not has_mandatory:
        audit_notes.append(f"Missing mandatory category attributes: {missing_mandatory}.")
    if not vision_ok:
        audit_notes.append(f"Vision agreement rate {vision_agreement_rate:.2f} below 0.50 threshold.")
    if ambiguity_flag:
        audit_notes.append("Ambiguous input: no brand or MPN identified, multiple products could match (generic specs applied).")

    if is_grounded and has_mandatory and vision_ok:
        note_msg = "All deterministic quality gates passed successfully."
        if ambiguity_flag:
            note_msg += " (Warning: Ambiguity flag active - generic attributes extracted)."
        return {
            "evaluator_decision": "accept",
            "missing_mandatory_attrs": [],
            "new_search_query": raw_input,
            "audit_notes": note_msg
        }

    # If quality checks failed:
    if retry_count < settings.MAX_RETRIES:
        # Formulate rewritten targeted query with industrial supplier domain hints
        missing = " ".join(missing_mandatory)
        rewritten_query = (
            f"{raw_input} {missing} "
            f"site:mcmaster.com OR site:grainger.com OR site:fastenal.com "
            f"OR site:rs-components.com OR site:digikey.com"
        ).strip()
        
        return {
            "evaluator_decision": "retry",
            "missing_mandatory_attrs": missing_mandatory,
            "new_search_query": rewritten_query,
            "audit_notes": f"Retry {retry_count + 1}/{settings.MAX_RETRIES}: " + "; ".join(audit_notes)
        }
    else:
        # Max retries reached -> escalate
        return {
            "evaluator_decision": "ask_user",
            "missing_mandatory_attrs": missing_mandatory,
            "new_search_query": raw_input,
            "audit_notes": f"Max retries ({settings.MAX_RETRIES}) reached. Escalating to human reviewer: " + "; ".join(audit_notes)
        }
