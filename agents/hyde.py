import logging
from typing import Dict, Any, Tuple
from llm.client import generate_text

logger = logging.getLogger("pimpulse.hyde")

async def expand_query_hyde(raw_input: str, category_name: str) -> Tuple[str, str, bool]:
    """
    Hypothetical Document Embeddings (HyDE) expansion for short or condensed industrial MPNs.
    Only triggers if len(raw_input) < 40 or no spaces.
    Returns: (expanded_query, hypothesis_text, is_expanded)
    """
    raw_clean = raw_input.strip()
    needs_expansion = len(raw_clean) < 40 or (" " not in raw_clean)

    if not needs_expansion:
        return raw_clean, "", False

    prompt = (
        f"You are an industrial catalog spec engineer.\n"
        f"Generate a concise 1-paragraph hypothetical technical spec-sheet excerpt for this industrial product part:\n"
        f"Part identifier: '{raw_clean}'\n"
        f"Likely category: '{category_name}'\n"
        f"Include likely key specifications, manufacturer naming conventions, operating values, and standards.\n"
        f"Keep it under 60 words."
    )
    
    hypothesis = await generate_text(prompt, temperature=0.2)
    hypothesis = hypothesis.strip()
    
    # Combined search query: original identifier + technical hypothesis
    expanded_query = f"{raw_clean} {hypothesis}"
    return expanded_query, hypothesis, True
