import json
import logging
from typing import List, Dict, Any
from llm.client import generate_json

logger = logging.getLogger("pimpulse.grading")

async def grade_documents_batched(
    raw_input: str,
    search_query: str,
    chunks: List[Dict[str, Any]],
    mandatory_attrs: List[str]
) -> List[Dict[str, Any]]:
    """
    Batched 1-call relevance grading.
    Instead of making N separate LLM calls, grades all candidate chunks in a single prompt.
    Returns the filtered list of relevant chunks.
    """
    if not chunks:
        return []

    chunks_formatted = []
    for i, c in enumerate(chunks):
        chunks_formatted.append(f"[Chunk {i}]: Title: {c.get('title', '')}\nContent: {c.get('content', '')[:300]}")

    formatted_text = "\n\n".join(chunks_formatted)
    
    prompt = (
        f"You are an industrial data relevance auditor.\n"
        f"Product Query: '{raw_input}'\n"
        f"Expanded Search: '{search_query}'\n"
        f"Target Mandatory Attributes: {mandatory_attrs}\n\n"
        f"Here are {len(chunks)} candidate retrieved chunks:\n"
        f"{formatted_text}\n\n"
        f"Task: Evaluate each chunk. Return a JSON object with 'passing_indices' containing the integer array of chunks that are genuinely relevant to the product specs.\n"
        f"Format: {{\"passing_indices\": [0, 1, ...]}}"
    )

    schema = "{\"passing_indices\": [0, 1]}"
    res = await generate_json(prompt, system_prompt="You are a strict technical document relevance evaluator.", schema_description=schema)
    
    passing_indices = res.get("passing_indices", [])
    if not isinstance(passing_indices, list):
        passing_indices = list(range(len(chunks)))
        
    graded_chunks = []
    for idx in passing_indices:
        if isinstance(idx, int) and 0 <= idx < len(chunks):
            graded_chunks.append(chunks[idx])
            
    # Fallback if over-filtered: keep at least top 2
    if not graded_chunks and chunks:
        graded_chunks = chunks[:2]
        
    return graded_chunks
