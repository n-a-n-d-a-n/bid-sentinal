"""Policy Intelligence & Copilot API Router."""
from typing import List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.policy import PolicySource, PolicyVersion, PolicyChunk
from app.models.user import User
from app.engines.policy.retriever import HybridPolicyRetriever
from app.engines.policy.ingestion import PolicyIngestionPipeline
from app.services.policy_copilot import PolicyCopilotService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/policy")

class QueryRequest(BaseModel):
    question: str
    source_filters: Optional[List[str]] = None
    version_filter: Optional[str] = None

class IngestRequest(BaseModel):
    source_code: str
    document_name: str
    authority: str
    version: str
    text_content: str
    document_type: str = "MANUAL"
    official_url: Optional[str] = None

class CompareRequest(BaseModel):
    source_a: str
    version_a: str
    source_b: str
    version_b: str
    topic: str

class BidPolicyExplanationRequest(BaseModel):
    requirement_name: str
    extracted_value: str
    required_value: str
    compliance_result: str

@router.post("/query")
async def query_policy(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    copilot = PolicyCopilotService(db)
    return await copilot.ask_policy(payload.question, payload.source_filters, payload.version_filter, user_id=current_user.id)

@router.get("/sources")
async def list_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(PolicySource))
    return res.scalars().all()

@router.get("/sources/{source_id}")
async def get_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(PolicySource).where(PolicySource.id == source_id))
    src = res.scalar_one_or_none()
    if not src:
        raise HTTPException(404, "Policy source not found.")
    return src

@router.get("/sources/{source_id}/versions")
async def get_source_versions(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(PolicyVersion).where(PolicyVersion.source_id == source_id))
    return res.scalars().all()

@router.get("/search")
async def search_policy(
    q: str = Query(..., min_length=2),
    source: Optional[str] = Query(None),
    version: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retriever = HybridPolicyRetriever(db)
    s_filter = [source] if source else None
    chunks = await retriever.retrieve(q, source_filter=s_filter, version_filter=version)
    return {"query": q, "results": chunks, "count": len(chunks)}

@router.post("/ingest", status_code=201)
async def ingest_policy(
    payload: IngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    pipeline = PolicyIngestionPipeline(db)
    ver = await pipeline.ingest_policy_document(
        source_code=payload.source_code,
        document_name=payload.document_name,
        authority=payload.authority,
        version=payload.version,
        text_content=payload.text_content,
        document_type=payload.document_type,
        official_url=payload.official_url,
    )
    return {"status": "INGESTED", "version_id": ver.id, "chunk_count": ver.chunk_count}

@router.get("/chunks/{chunk_id}")
async def get_chunk(
    chunk_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(PolicyChunk).where(PolicyChunk.id == chunk_id))
    chunk = res.scalar_one_or_none()
    if not chunk:
        raise HTTPException(404, "Policy chunk not found.")
    return chunk

@router.post("/compare")
async def compare_policies(
    payload: CompareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    copilot = PolicyCopilotService(db)
    return await copilot.compare_sources(payload.source_a, payload.version_a, payload.source_b, payload.version_b, payload.topic)

@router.post("/bids/{bid_id}/explanation")
async def get_bid_policy_explanation(
    bid_id: str,
    payload: BidPolicyExplanationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    copilot = PolicyCopilotService(db)
    return await copilot.generate_contextual_bidder_explanation(
        bid_id=bid_id,
        requirement_name=payload.requirement_name,
        extracted_value=payload.extracted_value,
        required_value=payload.required_value,
        compliance_result=payload.compliance_result,
    )
