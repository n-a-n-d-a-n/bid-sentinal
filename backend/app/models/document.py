"""Document, DocumentPage, and ExtractedField models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Polymorphic entity association
    entity_type: Mapped[str] = mapped_column(String(20))  # "bid" | "tender"
    entity_id: Mapped[str] = mapped_column(String(36), index=True)

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int | None] = mapped_column(Integer)
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True)

    # Storage
    storage_path: Mapped[str] = mapped_column(String(1000))  # MinIO path
    storage_bucket: Mapped[str] = mapped_column(String(100))

    # Classification
    document_type: Mapped[str] = mapped_column(String(100), default="OTHER")
    # GST_CERTIFICATE | PAN_DOCUMENT | UDYAM_CERTIFICATE | MCA_DOCUMENT |
    # FINANCIAL_STATEMENT | OEM_AUTHORIZATION | EXPERIENCE_CERTIFICATE |
    # BANK_GUARANTEE | DECLARATION | STARTUP_CERTIFICATE | MSME_DOCUMENT |
    # EPFO_DOCUMENT | ESIC_DOCUMENT | BLACKLIST_DOCUMENT | OTHER
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    classification_method: Mapped[str | None] = mapped_column(String(50))
    # "deterministic" | "keyword" | "llm" | "manual"

    # Processing status
    ocr_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    # PENDING | PROCESSING | COMPLETED | FAILED | LOW_CONFIDENCE
    ocr_engine: Mapped[str | None] = mapped_column(String(30))
    average_ocr_confidence: Mapped[float | None] = mapped_column(Float)
    extraction_status: Mapped[str] = mapped_column(String(30), default="PENDING")

    # Security
    security_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    # PENDING | CLEAN | FLAGGED | QUARANTINED
    is_corrupted: Mapped[bool] = mapped_column(Boolean, default=False)
    has_macros: Mapped[bool] = mapped_column(Boolean, default=False)
    has_scripts: Mapped[bool] = mapped_column(Boolean, default=False)

    # Demo flag
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)

    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    uploaded_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    pages: Mapped[list["DocumentPage"]] = relationship("DocumentPage", back_populates="document")
    extracted_fields: Mapped[list["ExtractedField"]] = relationship("ExtractedField", back_populates="document")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    bounding_boxes: Mapped[dict | None] = mapped_column(JSON)  # OCR word-level bboxes
    ocr_confidence: Mapped[float | None] = mapped_column(Float)
    ocr_engine: Mapped[str | None] = mapped_column(String(30))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    is_scanned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    document: Mapped["Document"] = relationship("Document", back_populates="pages")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    bid_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bids.id"), index=True)

    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_value: Mapped[str | None] = mapped_column(Text)
    field_value_normalized: Mapped[str | None] = mapped_column(Text)  # After normalization
    data_type: Mapped[str | None] = mapped_column(String(30))  # string | number | date | boolean

    confidence: Mapped[float | None] = mapped_column(Float)
    page_number: Mapped[int | None] = mapped_column(Integer)
    bounding_box: Mapped[dict | None] = mapped_column(JSON)  # {x, y, width, height}
    extraction_method: Mapped[str] = mapped_column(String(50))
    # "structured_llm_extraction" | "regex" | "heuristic" | "manual"

    # Validation
    validation_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    # PENDING | VALID | INVALID | REVIEW
    validation_error: Mapped[str | None] = mapped_column(Text)

    # Verification link
    verification_result_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("verification_results.id"))

    # Cross-document consistency
    consistency_status: Mapped[str | None] = mapped_column(String(20))
    # MATCH | CONFLICT | REVIEW | NOT_FOUND

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    document: Mapped["Document"] = relationship("Document", back_populates="extracted_fields")
