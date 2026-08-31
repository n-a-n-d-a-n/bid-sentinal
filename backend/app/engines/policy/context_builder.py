"""
RAG Context Builder.

Constructs bounded, formatted context from retrieved policy chunks.
"""
from typing import List
from app.engines.policy.retriever import RetrievedChunk

class ContextBuilderService:
    @staticmethod
    def build_context_text(chunks: List[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant policy passages retrieved."

        lines = ["--- RETRIEVED POLICY EVIDENCE ---"]
        for c in chunks:
            lines.append(
                f"[Source: {c.source_code} | Version: {c.version} | Section: {c.section} | Page: {c.page_number} | Chunk: {c.chunk_id[:8]}]\n{c.text}\n"
            )
        lines.append("--- END POLICY EVIDENCE ---")
        return "\n".join(lines)

context_builder = ContextBuilderService()
