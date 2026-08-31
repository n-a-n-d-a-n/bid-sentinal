"""
Policy Citation Engine.

Generates structured, verifiable citations from actual retrieved chunks.
Prevents hallucinated citations.
"""
from typing import List, Dict, Any
from app.engines.policy.retriever import RetrievedChunk

class CitationEngine:
    @staticmethod
    def generate_citations(chunks: List[RetrievedChunk]) -> List[Dict[str, Any]]:
        citations = []
        for c in chunks:
            citations.append({
                "source": c.source_code,
                "version": c.version,
                "section": c.section,
                "page": c.page_number,
                "chunk_id": c.chunk_id,
                "relevance": c.similarity,
            })
        return citations

citation_engine = CitationEngine()
