"""Tender and related models."""
import uuid
from datetime import UTC, datetime, date
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gem_bid_number: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(String(255))
    ministry: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(50), default="DRAFT"
    )  # DRAFT | ACTIVE | PROCESSING | REQUIREMENTS_EXTRACTED | CLOSED | CANCELLED
    estimated_value_inr: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    bid_submission_deadline: Mapped[date | None] = mapped_column(Date)
    technical_bid_opening: Mapped[date | None] = mapped_column(Date)
    financial_bid_opening: Mapped[date | None] = mapped_column(Date)
    published_date: Mapped[date | None] = mapped_column(Date)
    corrigendum_date: Mapped[date | None] = mapped_column(Date)
    requirements_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    requirements_approved_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    requirements_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    msme_applicable: Mapped[bool] = mapped_column(Boolean, default=False)
    startup_applicable: Mapped[bool] = mapped_column(Boolean, default=False)
    make_in_india: Mapped[bool] = mapped_column(Boolean, default=False)
    local_content_min_pct: Mapped[float | None] = mapped_column(Float)
    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    versions: Mapped[list["TenderVersion"]] = relationship("TenderVersion", back_populates="tender")
    requirements: Mapped[list["TenderRequirement"]] = relationship("TenderRequirement", back_populates="tender")
    documents: Mapped[list["Document"]] = relationship(
        "Document", primaryjoin="and_(Document.entity_type=='tender', Document.entity_id==Tender.id)",
        foreign_keys="[Document.entity_id]", overlaps="bid_documents",
    )
    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="tender")


class TenderVersion(Base):
    __tablename__ = "tender_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    change_type: Mapped[str] = mapped_column(String(50))  # CORRIGENDUM | AMENDMENT | ORIGINAL
    change_summary: Mapped[str | None] = mapped_column(Text)
    snapshot: Mapped[dict | None] = mapped_column(JSON)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    tender: Mapped["Tender"] = relationship("Tender", back_populates="versions")


class TenderRequirement(Base):
    __tablename__ = "tender_requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    requirement_id: Mapped[str] = mapped_column(String(100))  # structured ID like TURN_001
    category: Mapped[str] = mapped_column(String(100))  # FINANCIAL | TECHNICAL | EXPERIENCE | COMPLIANCE | DOCUMENT
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    rule_definition: Mapped[dict | None] = mapped_column(JSON)  # deterministic rule JSON
    source_document: Mapped[str | None] = mapped_column(String(255))
    source_page: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_until: Mapped[date | None] = mapped_column(Date)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    officer_notes: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    tender: Mapped["Tender"] = relationship("Tender", back_populates="requirements")
    rule_evaluations: Mapped[list["RuleEvaluation"]] = relationship("RuleEvaluation", back_populates="requirement")
