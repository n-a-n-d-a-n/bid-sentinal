"""
Hybrid Policy Retriever Engine.

Combines:
1. Cosine vector similarity search
2. Keyword matching
3. Metadata filtering (source, version, section)
"""
import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import PolicySource, PolicyVersion, PolicyChunk
from app.engines.policy.embedding import embedding_provider

logger = structlog.get_logger(__name__)

class RetrievedChunk:
    def __init__(
        self,
        chunk_id: str,
        source_code: str,
        version: str,
        section: str,
        page_number: int,
        text: str,
        similarity: float,
        rank: int = 0,
    ):
        self.chunk_id = chunk_id
        self.source_code = source_code
        self.version = version
        self.section = section
        self.page_number = page_number
        self.text = text
        self.similarity = similarity
        self.rank = rank

class HybridPolicyRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve(
        self,
        question: str,
        source_filter: Optional[List[str]] = None,
        version_filter: Optional[str] = None,
        top_k: int = 5,
    ) -> List[RetrievedChunk]:
        query_vec = embedding_provider.generate_embedding(question)
        q_words = set(w.lower() for w in question.split() if len(w) > 3)

        # Query chunks with joined source & version
        stmt = (
            select(PolicyChunk, PolicyVersion, PolicySource)
            .join(PolicyVersion, PolicyChunk.version_id == PolicyVersion.id)
            .join(PolicySource, PolicyVersion.source_id == PolicySource.id)
        )
        if source_filter:
            stmt = stmt.where(PolicySource.source_code.in_(source_filter))
        if version_filter:
            stmt = stmt.where(PolicyVersion.version == version_filter)

        res = await self.db.execute(stmt)
        rows = res.all()

        scored_chunks: List[RetrievedChunk] = []

        for chunk_inst, version_inst, source_inst in rows:
            chunk_vec = embedding_provider.deserialize_vector(chunk_inst.embedding)
            sim = embedding_provider.cosine_similarity(query_vec, chunk_vec) if chunk_vec else 0.50

            # Keyword bonus
            c_text_lower = chunk_inst.text.lower()
            keyword_overlap = sum(1 for w in q_words if w in c_text_lower)
            keyword_bonus = min(0.30, keyword_overlap * 0.08)

            final_score = round(min(1.0, sim + keyword_bonus), 4)

            scored_chunks.append(RetrievedChunk(
                chunk_id=chunk_inst.id,
                source_code=source_inst.source_code,
                version=version_inst.version,
                section=chunk_inst.section or "General Provision",
                page_number=chunk_inst.page_number or 1,
                text=chunk_inst.text,
                similarity=final_score,
            ))

        # Sort by similarity score descending
        scored_chunks.sort(key=lambda x: x.similarity, reverse=True)
        top_chunks = scored_chunks[:top_k]

        for i, c in enumerate(top_chunks):
            c.rank = i + 1

        logger.info("policy_retrieval_complete", question=question[:50], count=len(top_chunks))
        return top_chunks

hybrid_policy_retriever = HybridPolicyRetriever
