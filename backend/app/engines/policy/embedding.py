"""
Embedding Provider Abstraction & Vector Operations.

Supports:
- Cosine similarity calculation
- Configurable vector dimensions (default: 384 for sentence-transformers / 1536 for OpenAI)
- Vector serialization to JSON strings for SQLite/PostgreSQL pgvector compatibility
"""
import json
import math
import structlog
from typing import List, Dict, Any, Optional

logger = structlog.get_logger(__name__)

class EmbeddingProviderService:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.embedding_model = "all-MiniLM-L6-v2-mock"
        self.embedding_version = "v1.0"

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates deterministic pseudo-embedding vector for text (or calls model if available).
        """
        if not text:
            return [0.0] * self.dimension

        # Simple deterministic hashing to unit vector of self.dimension
        vec = [0.0] * self.dimension
        for i, char in enumerate(text[:500]):
            idx = (ord(char) * (i + 1)) % self.dimension
            vec[idx] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return round(dot / (norm1 * norm2), 4)

    @staticmethod
    def serialize_vector(vector: List[float]) -> str:
        return json.dumps(vector)

    @staticmethod
    def deserialize_vector(vector_str: Optional[str]) -> List[float]:
        if not vector_str:
            return []
        try:
            return json.loads(vector_str)
        except Exception:
            return []

embedding_provider = EmbeddingProviderService()
