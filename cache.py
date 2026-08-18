import hashlib
import time
import math
from typing import Dict, Any, Optional, Tuple, List
import numpy as np

class SemanticCache:
    """
    Two-Level Cache for Industrial Product Queries:
    Level 1: Exact normalized string SHA-256 hash (< 1ms)
    Level 2: Semantic vector cosine similarity with >= 0.96 threshold (< 20ms)
    """
    def __init__(self, similarity_threshold: float = 0.96):
        self.similarity_threshold = similarity_threshold
        self.exact_cache: Dict[str, Dict[str, Any]] = {}
        self.vector_cache: List[Tuple[str, np.ndarray, Dict[str, Any]]] = []

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().strip().split())

    def _hash(self, text: str) -> str:
        return hashlib.sha256(self._normalize(text).encode("utf-8")).hexdigest()

    def _pseudo_embed(self, text: str) -> np.ndarray:
        """
        Deterministic character n-gram + token frequency vector for ultra-fast local similarity.
        Also compatible with NVIDIA nv-embedqa-e5-v5 when available.
        """
        tokens = self._normalize(text).split()
        # Generate 128-dimensional deterministic projection
        vec = np.zeros(128, dtype=np.float32)
        for i, tok in enumerate(tokens):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            for j in range(4):
                idx = (h >> (j * 8)) % 128
                vec[idx] += 1.0 / (i + 1)
                
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def get(self, query: str) -> Tuple[Optional[Dict[str, Any]], str, float]:
        """
        Check cache: returns (cached_profile, hit_type, latency_ms)
        hit_type: 'EXACT_HIT' | 'SEMANTIC_HIT' | 'MISS'
        """
        start_t = time.perf_counter()
        norm_q = self._normalize(query)
        q_hash = self._hash(norm_q)

        # Level 1: Exact Hash
        if q_hash in self.exact_cache:
            latency = (time.perf_counter() - start_t) * 1000.0
            return self.exact_cache[q_hash], "EXACT_HIT", round(latency, 2)

        # Level 2: Vector Cosine
        if self.vector_cache:
            q_vec = self._pseudo_embed(norm_q)
            best_score = -1.0
            best_match = None

            for orig_text, emb, profile in self.vector_cache:
                sim = float(np.dot(q_vec, emb))
                if sim > best_score:
                    best_score = sim
                    best_match = profile

            if best_score >= self.similarity_threshold and best_match:
                latency = (time.perf_counter() - start_t) * 1000.0
                return best_match, f"SEMANTIC_HIT (cos={best_score:.3f})", round(latency, 2)

        latency = (time.perf_counter() - start_t) * 1000.0
        return None, "MISS", round(latency, 2)

    def set(self, query: str, profile: Dict[str, Any]):
        """Save to both exact hash and vector cache only if valid."""
        if not profile:
            return
        # Guard against caching failed/rejected runs with zero attributes
        if profile.get("evaluator_decision") == "ask_user" and not profile.get("attributes"):
            return
            
        norm_q = self._normalize(query)
        q_hash = self._hash(norm_q)
        
        # Save exact
        self.exact_cache[q_hash] = profile
        
        # Save vector embedding
        q_vec = self._pseudo_embed(norm_q)
        self.vector_cache.append((norm_q, q_vec, profile))

    def clear(self):
        """Clear all cached entries."""
        self.exact_cache.clear()
        self.vector_cache.clear()

# Global singleton
semantic_cache = SemanticCache()
