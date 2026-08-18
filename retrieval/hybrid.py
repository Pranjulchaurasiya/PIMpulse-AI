from typing import List, Dict, Any, Tuple

def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60,
    top_n: int = 8
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Reciprocal Rank Fusion (RRF) algorithm (Cormack et al., 2009).
    rrf_score(d) = sum(1 / (k + rank(d, list_i)))
    Rank is 1-indexed.
    
    Returns: (fused_chunks, multi_source_agreement_rate)
    """
    scores: Dict[str, float] = {}
    chunk_store: Dict[str, Dict[str, Any]] = {}
    source_presence: Dict[str, set] = {}

    for list_idx, chunk_list in enumerate(ranked_lists):
        source_name = f"list_{list_idx}"
        for rank_zero, chunk in enumerate(chunk_list):
            chunk_id = chunk.get("id") or str(hash(chunk.get("content", "")))
            rank = rank_zero + 1
            
            if chunk_id not in scores:
                scores[chunk_id] = 0.0
                chunk_store[chunk_id] = chunk
                source_presence[chunk_id] = set()

            scores[chunk_id] += 1.0 / (k + rank)
            source_presence[chunk_id].add(source_name)

    # Sort chunks by descending RRF score
    sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)[:top_n]
    
    fused_chunks = []
    agreement_count = 0
    num_lists = len([l for l in ranked_lists if len(l) > 0])

    for cid in sorted_chunk_ids:
        chunk_data = dict(chunk_store[cid])
        chunk_data["rrf_score"] = round(scores[cid], 5)
        # Check if chunk appeared in multiple non-empty sources
        if len(source_presence[cid]) > 1:
            agreement_count += 1
            chunk_data["multi_source"] = True
        else:
            chunk_data["multi_source"] = False
        fused_chunks.append(chunk_data)

    # Multi-source agreement rate: ratio of top fused chunks present in both web and vector
    agreement_rate = (agreement_count / len(fused_chunks)) if (fused_chunks and num_lists > 1) else 0.0
    return fused_chunks, round(agreement_rate, 3)
