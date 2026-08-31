"""
Deterministic Policy Reranker.
"""
from typing import List
from app.engines.policy.retriever import RetrievedChunk

class PolicyRerankerService:
    def rerank(self, chunks: List[RetrievedChunk], question: str) -> List[RetrievedChunk]:
        if not chunks:
            return []

        # Rerank by similarity score and page order
        reranked = sorted(chunks, key=lambda x: (x.similarity, -x.page_number), reverse=True)
        for i, c in enumerate(reranked):
            c.rank = i + 1
        return reranked

policy_reranker = PolicyRerankerService()
