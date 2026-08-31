"""Policy knowledge base models for RAG."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PolicySource(Base):
    __tablename__ = "policy_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    authority: Mapped[str] = mapped_column(String(255), nullable=False)
    document_name: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100))
    # GTC | ATC | STC | MANUAL | NOTIFICATION | ACT | RULE
    official_url: Mapped[str | None] = mapped_column(String(1000))
    current_version: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE | SUPERSEDED | REPEALED
    sector: Mapped[str | None] = mapped_column(String(100))
    approved_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    versions: Mapped[list["PolicyVersion"]] = relationship("PolicyVersion", back_populates="source")


class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("policy_sources.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    published_date: Mapped[str | None] = mapped_column(String(20))
    effective_from: Mapped[str | None] = mapped_column(String(20))
    effective_until: Mapped[str | None] = mapped_column(String(20))
    document_hash: Mapped[str | None] = mapped_column(String(64))
    storage_path: Mapped[str | None] = mapped_column(String(1000))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    source: Mapped["PolicySource"] = relationship("PolicySource", back_populates="versions")
    chunks: Mapped[list["PolicyChunk"]] = relationship("PolicyChunk", back_populates="version")


class PolicyChunk(Base):
    __tablename__ = "policy_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("policy_versions.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str | None] = mapped_column(Text)  # JSON-serialized vector (pgvector in production)
    page_number: Mapped[int | None] = mapped_column(Integer)
    clause_id: Mapped[str | None] = mapped_column(String(100))
    keywords: Mapped[dict | None] = mapped_column(JSON)
    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    version: Mapped["PolicyVersion"] = relationship("PolicyVersion", back_populates="chunks")
