import logging
import threading
from typing import Dict, Any

logger = logging.getLogger("pimpulse.cost_tracker")

# Groq / Open source LPU pricing (approx): Llama 3.1 8B ~$0.05/1M, Llama 3.3 70B ~$0.59/1M input, $0.79/1M output
COST_PER_1K_INPUT = 0.00059
COST_PER_1K_OUTPUT = 0.00079

_lock = threading.Lock()
_session_tokens = {
    "input": 0,
    "output": 0,
    "calls": 0,
    "skus_processed": 0
}

def track_call(input_tokens: int, output_tokens: int):
    """Increment token counters in a thread-safe manner."""
    with _lock:
        _session_tokens["input"] += max(input_tokens, 0)
        _session_tokens["output"] += max(output_tokens, 0)
        _session_tokens["calls"] += 1

def record_sku_processed():
    """Increment processed SKU count."""
    with _lock:
        _session_tokens["skus_processed"] += 1

def get_cost_summary() -> Dict[str, Any]:
    """Calculate and return real-time session cost and cost per SKU."""
    with _lock:
        in_toks = _session_tokens["input"]
        out_toks = _session_tokens["output"]
        calls = _session_tokens["calls"]
        skus = max(_session_tokens["skus_processed"], 1)

    input_cost = (in_toks / 1000.0) * COST_PER_1K_INPUT
    output_cost = (out_toks / 1000.0) * COST_PER_1K_OUTPUT
    total_cost = input_cost + output_cost
    cost_per_sku = total_cost / skus

    return {
        "total_calls": calls,
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "skus_processed": _session_tokens["skus_processed"],
        "cost_usd": round(total_cost, 6),
        "cost_per_sku_usd": round(cost_per_sku, 6),
        "cost_formatted": f"${total_cost:.5f}",
        "cost_per_sku_formatted": f"${cost_per_sku:.5f}/SKU"
    }

def reset_tracker():
    """Reset session counters."""
    with _lock:
        _session_tokens["input"] = 0
        _session_tokens["output"] = 0
        _session_tokens["calls"] = 0
        _session_tokens["skus_processed"] = 0
