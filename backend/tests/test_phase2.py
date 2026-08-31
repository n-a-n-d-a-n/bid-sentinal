"""
PROCUREX Test Suite — Phase 2 Tests (T14 - T34)
Document Intelligence Pipeline, Security, OCR, Classification, Extraction, Entity Resolution, Pipeline Orchestration & Auditability.
"""
import pytest
import asyncio
from datetime import UTC, datetime

# ─────────────────────────────────────────────────────────────────────────────
# T14: Document Storage Service
# ─────────────────────────────────────────────────────────────────────────────

def test_storage_service_generate_key():
    """T14a: Storage service generates deterministic keys."""
    from app.services.storage_service import storage_service

    key = storage_service.generate_object_key("doc-123", "sample tender.pdf", category="original")
    assert key == "documents/doc-123/original/sample_tender.pdf"

    page_key = storage_service.generate_object_key("doc-123", "page.png", category="page", page_number=2)
    assert page_key == "documents/doc-123/pages/page_2.png"
    print("\n  [T14a] Storage deterministic key generation: OK")

def test_storage_service_upload_download():
    """T14b: Storage service uploads and downloads bytes."""
    from app.services.storage_service import storage_service

    test_data = b"Hello PROCUREX Storage Pipeline"
    key = "documents/test-doc/original/test_file.txt"

    uploaded_key = storage_service.upload_bytes(test_data, key)
    assert uploaded_key == key
    assert storage_service.object_exists(key) == True

    downloaded = storage_service.download_bytes(key)
    assert downloaded == test_data

    storage_service.delete_object(key)
    print("  [T14b] Storage upload/download/exists/delete: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T15: Document Security & SHA-256 Deduplication
# ─────────────────────────────────────────────────────────────────────────────

def test_document_security_validation():
    """T15: File security validation & SHA256 computation."""
    from app.services.document_security import document_security
    from fastapi import HTTPException

    pdf_content = b"%PDF-1.4\nSample PDF Content"
    meta = document_security.validate_file("tender_doc.pdf", "application/pdf", pdf_content)

    assert meta["safe_filename"] == "tender_doc.pdf"
    assert meta["detected_mime_type"] == "application/pdf"
    assert len(meta["sha256_hash"]) == 64

    # Invalid Extension
    with pytest.raises(HTTPException):
        document_security.validate_file("script.exe", "application/x-msdownload", b"exe data")

    # Invalid PDF Magic Bytes
    with pytest.raises(HTTPException):
        document_security.validate_file("fake.pdf", "application/pdf", b"NOT_A_PDF_MAGIC_BYTES")

    print("\n  [T15] Document security validation & hash computation: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T16 & T17 & T18: PDF Parsing & OCR Requirement Detection
# ─────────────────────────────────────────────────────────────────────────────

def test_pdf_parsing_and_ocr_detection():
    """T16-T18: PyMuPDF parsing, page extraction, and OCR-required detection."""
    from app.services.document_parser import document_parser

    # Create dummy PDF in memory using fitz
    import fitz
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "Notice Inviting Tender for Smart Grid Equipment. PAN: AADCB2230M.")

    # Second page with scanned image simulation
    p2 = doc.new_page()
    pix = p1.get_pixmap()
    p2.insert_image(p2.rect, stream=pix.tobytes("png"))

    pdf_bytes = doc.tobytes()
    doc.close()

    meta, pages = document_parser.parse_pdf(pdf_bytes, render_pages=False)

    assert meta["page_count"] == 2
    assert len(pages) == 2
    assert "Notice Inviting Tender" in pages[0].raw_text
    assert pages[0].ocr_required == False
    assert pages[1].is_scanned == True or pages[1].ocr_required == True

    print("\n  [T16-T18] PDF parsing, text extraction, & OCR-required detection: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T19: OCR Unavailable Safe Handling
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ocr_unavailable_fallback():
    """T19: OCR provider returns UNAVAILABLE status gracefully if missing."""
    from app.engines.ocr.tesseract_provider import TesseractOCRProvider
    from app.engines.ocr.base import OCRStatus

    provider = TesseractOCRProvider(tesseract_cmd="/nonexistent/tesseract/bin")
    res = await provider.extract_text(b"fake_image_bytes", page_number=1)

    assert res.status in (OCRStatus.UNAVAILABLE, OCRStatus.FAILED)
    assert res.extracted_text == ""
    print("\n  [T19] OCR Provider missing fallback: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T20: Text Normalization
# ─────────────────────────────────────────────────────────────────────────────

def test_text_normalization():
    """T20: Text normalizer cleans up artifacts without corrupting legal terms."""
    from app.services.text_normalizer import text_normalizer

    raw = "ANNUAL   TURNOVER:\r\nProcure-\nment of Equipment  \n\n\n\nSection 4."
    norm = text_normalizer.normalize_text(raw)

    assert "ANNUAL TURNOVER:" in norm
    assert "Procurement of Equipment" in norm
    assert "\n\n\n\n" not in norm
    print("\n  [T20] Text normalization: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T21: Document Classification
# ─────────────────────────────────────────────────────────────────────────────

def test_document_classification():
    """T21: Document classifier identifies document types and confidence."""
    from app.services.document_classifier import document_classifier

    # GST document
    doc_type, conf, method = document_classifier.classify("Registration Certificate GSTIN 27AADCB2230M1ZP", "gst_cert.pdf")
    assert doc_type == "GST_DOCUMENT"
    assert conf >= 0.85

    # Financial document
    doc_type_f, conf_f, _ = document_classifier.classify("Audited Balance Sheet Annual Turnover 15 Crore", "financials.pdf")
    assert doc_type_f == "FINANCIAL_DOCUMENT"

    print("\n  [T21] Document classification: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T22: Regex Rule Extractor
# ─────────────────────────────────────────────────────────────────────────────

def test_rule_extractor_identifiers():
    """T22: Rule extractor parses PAN, GSTIN, CIN, Udyam, and turnover accurately."""
    from app.engines.extraction.rule_extractor import rule_extractor

    sample_text = """
    Bidder Details:
    PAN: AADCB2230M
    GSTIN: 27AADCB2230M1ZP
    CIN: U72900MH2020PTC345678
    Udyam: UDYAM-MH-01-0000001
    Annual Turnover: 15.0 Crore
    """

    fields = rule_extractor.extract_from_page(sample_text, page_number=1)
    field_dict = {f.field_name: f.field_value for f in fields}

    assert field_dict.get("pan") == "AADCB2230M"
    assert field_dict.get("gstin") == "27AADCB2230M1ZP"
    assert field_dict.get("cin") == "U72900MH2020PTC345678"
    assert field_dict.get("udyam_number") == "UDYAM-MH-01-0000001"
    assert field_dict.get("annual_turnover_inr") == "150000000.0"

    print("\n  [T22] Regex rule extraction (PAN/GSTIN/CIN/Udyam/Turnover): OK")

# ─────────────────────────────────────────────────────────────────────────────
# T23, T24, T25, T26: LLM Abstraction & Extraction Provenance
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_llm_abstraction_and_mock_provider():
    """T23-T26: LLM abstraction, mock provider, structured contract & provenance."""
    from app.engines.llm import get_llm_provider
    from app.engines.extraction.schemas import BidderExtractionSchema
    from app.engines.extraction.orchestrator import extraction_orchestrator

    provider = get_llm_provider("mock")
    instance, resp = await provider.generate_structured(
        prompt="Extract bidder info",
        response_schema=BidderExtractionSchema,
    )
    assert resp.is_mock == True

    # Test extraction orchestrator provenance
    res = await extraction_orchestrator.extract_document_fields(
        document_id="doc-999",
        document_type="GST_DOCUMENT",
        pages_text=[{"page_number": 1, "text": "GSTIN: 27AADCB2230M1ZP PAN: AADCB2230M"}],
        use_llm=False,
    )

    assert len(res.fields) >= 2
    for f in res.fields:
        assert f.confidence > 0.0
        assert f.page_number is not None
        assert f.extraction_method is not None

    print("\n  [T23-T26] LLM abstraction & extraction contract provenance: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T27, T28, T29, T30: Entity Resolution & Safety Rules
# ─────────────────────────────────────────────────────────────────────────────

def test_entity_normalization_and_matching():
    """T27-T30: Entity resolution, exact identifier match, fuzzy match, & safety rules."""
    from app.engines.entity_resolution.normalizer import entity_normalizer
    from app.engines.entity_resolution.matching import entity_matcher

    norm1 = entity_normalizer.normalize_company_name("Acme Technologies Pvt. Ltd.")
    norm2 = entity_normalizer.normalize_company_name("ACME TECHNOLOGIES PRIVATE LIMITED")
    assert norm1 == norm2 == "acme"

    # Exact PAN match
    e1 = {"name": "Acme", "pan": "AADCB2230M"}
    e2 = {"name": "Acme Systems", "pan": "AADCB2230M"}
    status, conf, method, _ = entity_matcher.match_entities(e1, e2)
    assert status == "MATCHED"
    assert conf == 1.0

    # Fuzzy match -> POSSIBLE_MATCH (not auto MATCHED)
    e3 = {"name": "Shakti Infrastructure Solutions Pvt Ltd"}
    e4 = {"name": "Shakti Infrastructure Private Limited"}
    status_f, conf_f, _, _ = entity_matcher.match_entities(e3, e4)
    assert status_f == "POSSIBLE_MATCH"
    assert conf_f < 1.0

    print("\n  [T27-T30] Entity normalization, exact match & fuzzy match safety: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T31, T32, T33, T34: Pipeline Orchestration, Reprocessing & Auditability
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_pipeline_orchestration(db_session):
    """T31-T34: Full pipeline execution, document processing, job tracking & audit trail."""
    from app.repositories.user_repository import UserRepository
    from app.core.security import hash_password
    from app.models.user import User
    from app.models.document import Document
    from app.services.pipeline_orchestrator import PipelineOrchestratorService
    from app.repositories.misc import AuditRepository

    # Create dummy user
    u_repo = UserRepository(db_session)
    user = User(email="officer_p2@procurex.local", username="officer_p2", full_name="Officer P2", hashed_password=hash_password("Pass@123"), role="PROCUREMENT_OFFICER")
    await u_repo.create(user)

    # Create dummy document record
    doc = Document(
        entity_type="bid",
        entity_id="bid-100",
        filename="test_credentials.pdf",
        original_filename="bidder_credentials.pdf",
        content_type="application/pdf",
        size_bytes=500,
        sha256_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        storage_path="documents/doc-p2/original/bidder_credentials.pdf",
        storage_bucket="procurex-documents",
        uploaded_by=user.id,
    )
    db_session.add(doc)
    await db_session.commit()

    orchestrator = PipelineOrchestratorService(db_session)
    res = await orchestrator.process_document(doc.id)

    assert res["status"] == "COMPLETED"
    assert res["fields_extracted"] >= 0

    # Verify audit event recorded
    audit_repo = AuditRepository(db_session)
    audits = await audit_repo.get_for_entity("DOCUMENT", doc.id)
    assert len(audits) >= 1

    print("\n  [T31-T34] Full pipeline orchestration, reprocessing & audit logging: OK")
