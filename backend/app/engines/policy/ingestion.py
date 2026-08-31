"""
Policy Ingestion Pipeline.

Ingests policy PDFs & manuals into PolicySource, PolicyVersion, and PolicyChunk database records.
Uses SHA-256 checksum deduplication to avoid re-indexing unchanged documents.
"""
import hashlib
import structlog
from typing import Dict, Any, List, Optional
from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.policy import PolicySource, PolicyVersion, PolicyChunk
from app.engines.policy.parser import policy_parser
from app.engines.policy.chunker import policy_chunker
from app.engines.policy.embedding import embedding_provider

logger = structlog.get_logger(__name__)

class PolicyIngestionPipeline:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_policy_document(
        self,
        source_code: str,
        document_name: str,
        authority: str,
        version: str,
        text_content: str,
        document_type: str = "MANUAL",
        official_url: Optional[str] = None,
    ) -> PolicyVersion:
        doc_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()

        # 1. Get or Create PolicySource
        src_res = await self.db.execute(select(PolicySource).where(PolicySource.source_code == source_code))
        source: Optional[PolicySource] = src_res.scalar_one_or_none()

        if not source:
            source = PolicySource(
                source_code=source_code,
                authority=authority,
                document_name=document_name,
                document_type=document_type,
                official_url=official_url,
                current_version=version,
                status="ACTIVE",
            )
            self.db.add(source)
            await self.db.flush()

        # 2. Check for duplicate version hash
        ver_res = await self.db.execute(
            select(PolicyVersion).where(PolicyVersion.source_id == source.id, PolicyVersion.version == version)
        )
        existing_ver: Optional[PolicyVersion] = ver_res.scalar_one_or_none()

        if existing_ver and existing_ver.document_hash == doc_hash:
            logger.info("policy_ingestion_skipped_duplicate", source_code=source_code, version=version)
            return existing_ver

        if not existing_ver:
            existing_ver = PolicyVersion(
                source_id=source.id,
                version=version,
                published_date="2017-01-01",
                effective_from="2017-01-01",
                document_hash=doc_hash,
                is_current=True,
            )
            self.db.add(existing_ver)
            await self.db.flush()

        # 3. Parse & Chunk Content
        sections = policy_parser.parse_text(text_content)
        chunks = policy_chunker.chunk_sections(sections)

        # 4. Save Chunks with Embeddings
        chunk_models = []
        for c in chunks:
            vec = embedding_provider.generate_embedding(c.text)
            vec_json = embedding_provider.serialize_vector(vec)

            chunk_inst = PolicyChunk(
                version_id=existing_ver.id,
                chunk_index=c.chunk_index,
                section=c.section,
                clause_id=c.clause_id,
                page_number=c.page_number,
                text=c.text,
                embedding=vec_json,
                keywords={"words": c.keywords},
                metadata_={"source_code": source_code, "version": version, "checksum": c.checksum},
            )
            self.db.add(chunk_inst)
            chunk_models.append(chunk_inst)

        existing_ver.chunk_count = len(chunk_models)
        await self.db.commit()

        logger.info("policy_ingestion_complete", source_code=source_code, version=version, chunk_count=len(chunk_models))
        return existing_ver

policy_ingestion_pipeline = PolicyIngestionPipeline
