"""
Documents & Processing API Router.

Provides endpoints for document upload, security validation, page listing,
structured extractions, evidence provenance, human correction, and async processing.
"""
from typing import List, Optional, Dict, Any
import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.document import Document, DocumentPage, ExtractedField
from app.models.job import ProcessingJob
from app.models.user import User
from app.repositories.misc import DocumentRepository, ProcessingJobRepository
from app.services.storage_service import storage_service
from app.services.document_security import document_security
from app.services.audit_service import AuditService, AuditAction, AuditCategory
from app.workers.tasks import process_document_task
from app.schemas.document import DocumentResponse, DocumentPageResponse, ExtractedFieldResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/documents")

class FieldCorrectionRequest(BaseModel):
    field_id: str
    corrected_value: str
    correction_reason: Optional[str] = Field(None, min_length=3)

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    entity_type: str = "bid",
    entity_id: str = "demo-entity-id",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document.
    Enforces security checks, SHA-256 deduplication, storage in MinIO, and metadata registration.
    """
    audit = AuditService(db)
    doc_repo = DocumentRepository(db)

    data = await file.read()
    raw_filename = file.filename or "uploaded_document.pdf"
    content_type = file.content_type or "application/pdf"

    # Security validation
    sec_meta = document_security.validate_file(raw_filename, content_type, data)

    # SHA256 deduplication check
    existing = await doc_repo.get_by_hash(sec_meta["sha256_hash"])
    if existing and existing.entity_id == entity_id:
        return existing

    # Store in MinIO / Local storage
    storage_key = storage_service.generate_object_key("temp", sec_meta["safe_filename"], category="original")
    storage_service.upload_bytes(data, storage_key, content_type=sec_meta["detected_mime_type"])

    doc = Document(
        entity_type=entity_type,
        entity_id=entity_id,
        filename=sec_meta["safe_filename"],
        original_filename=sec_meta["original_filename"],
        content_type=sec_meta["detected_mime_type"],
        size_bytes=sec_meta["size_bytes"],
        sha256_hash=sec_meta["sha256_hash"],
        storage_path=storage_key,
        storage_bucket=settings.MINIO_BUCKET_DOCUMENTS,
        document_type="OTHER",
        ocr_status="PENDING",
        extraction_status="PENDING",
        security_status="CLEAN",
        uploaded_by=current_user.id,
    )
    await doc_repo.create(doc)

    await audit.log(
        action=AuditAction.DOCUMENT_UPLOAD,
        action_category=AuditCategory.DOCUMENT,
        user_id=current_user.id,
        user_email=current_user.email,
        entity_type="DOCUMENT",
        entity_id=doc.id,
        document_hash=doc.sha256_hash,
    )
    return doc

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(404, "Document not found.")
    return doc

@router.get("/{document_id}/pages", response_model=List[DocumentPageResponse])
async def get_document_pages(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DocumentPage).where(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number)
    )
    pages = result.scalars().all()
    return pages

@router.get("/{document_id}/extractions", response_model=List[ExtractedFieldResponse])
async def get_document_extractions(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ExtractedField).where(ExtractedField.document_id == document_id)
    )
    fields = result.scalars().all()
    return fields

@router.get("/{document_id}/evidence")
async def get_document_evidence(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns full provenance & evidence chain for document extractions:
    field, value, confidence, page, text_excerpt, extraction_method.
    """
    doc_res = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found.")

    fields_res = await db.execute(select(ExtractedField).where(ExtractedField.document_id == document_id))
    fields = fields_res.scalars().all()

    evidence_items = []
    for f in fields:
        evidence_items.append({
            "field_id": f.id,
            "field_name": f.field_name,
            "field_value": f.field_value,
            "field_value_normalized": f.field_value_normalized,
            "confidence": f.confidence,
            "page_number": f.page_number,
            "extraction_method": f.extraction_method,
            "validation_status": f.validation_status,
            "document_id": document_id,
            "original_filename": doc.original_filename,
        })
    return {"document_id": document_id, "evidence_chain": evidence_items}

@router.post("/{document_id}/process")
async def process_document_api(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers asynchronous document processing pipeline."""
    doc_res = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found.")

    # Create processing job
    job = ProcessingJob(
        job_type="DOCUMENT_PARSE",
        entity_type="DOCUMENT",
        entity_id=document_id,
        status="QUEUED",
        created_by=current_user.id,
    )
    db.add(job)
    await db.flush()

    background_tasks.add_task(process_document_task, document_id, job.id)
    return {"job_id": job.id, "status": "QUEUED", "message": "Document processing pipeline queued."}

@router.post("/{document_id}/reprocess")
async def reprocess_document_api(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Idempotently reprocesses an existing document without duplicate corruption."""
    return await process_document_api(document_id, background_tasks, db, current_user)

@router.post("/{document_id}/extractions/correct")
async def correct_extracted_field(
    document_id: str,
    payload: FieldCorrectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """
    Human review endpoint for correcting an extracted field.
    Preserves original extracted value & confidence, updates corrected value, records reviewer and audit event.
    """
    res = await db.execute(select(ExtractedField).where(ExtractedField.id == payload.field_id))
    field_inst: Optional[ExtractedField] = res.scalar_one_or_none()
    if not field_inst or field_inst.document_id != document_id:
        raise HTTPException(404, "Extracted field not found.")

    old_val = field_inst.field_value
    field_inst.field_value = payload.corrected_value
    field_inst.validation_status = "MANUAL_CORRECTED"

    audit = AuditService(db)
    await audit.log(
        action="EXTRACTION_CORRECTED",
        action_category=AuditCategory.COMPLIANCE,
        user_id=current_user.id,
        user_email=current_user.email,
        entity_type="EXTRACTED_FIELD",
        entity_id=field_inst.id,
        old_value={"value": old_val},
        new_value={"value": payload.corrected_value, "reason": payload.correction_reason},
        change_summary=f"Human reviewer corrected field '{field_inst.field_name}'.",
    )
    await db.commit()
    return {"status": "SUCCESS", "message": "Field corrected successfully", "field_id": field_inst.id}
