"""Bidder canonical entity models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Bidder(Base):
    __tablename__ = "bidders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(500))
    trade_name: Mapped[str | None] = mapped_column(String(500))
    entity_type: Mapped[str | None] = mapped_column(String(100))  # COMPANY | PARTNERSHIP | PROPRIETORSHIP | LLP
    pan: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    gstin: Mapped[str | None] = mapped_column(String(20), index=True)  # Primary GSTIN (may have multiples)
    cin: Mapped[str | None] = mapped_column(String(25), unique=True, index=True)
    udyam_number: Mapped[str | None] = mapped_column(String(30), index=True)
    gem_seller_id: Mapped[str | None] = mapped_column(String(100))
    registered_address: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(String(100))
    pincode: Mapped[str | None] = mapped_column(String(10))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    incorporation_date: Mapped[str | None] = mapped_column(String(20))  # ISO date string
    directors: Mapped[dict | None] = mapped_column(JSON)  # List of director objects
    msme_category: Mapped[str | None] = mapped_column(String(20))  # MICRO | SMALL | MEDIUM
    is_startup: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)
    blacklist_reference: Mapped[str | None] = mapped_column(Text)
    resolution_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    resolution_method: Mapped[str | None] = mapped_column(String(100))
    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    identifiers: Mapped[list["BidderIdentifier"]] = relationship("BidderIdentifier", back_populates="bidder")
    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="bidder")
    graph_entities: Mapped[list["GraphEntity"]] = relationship(
        "GraphEntity", primaryjoin="and_(GraphEntity.entity_type=='COMPANY', GraphEntity.entity_ref_id==Bidder.id)",
        foreign_keys="[GraphEntity.entity_ref_id]",
    )


class BidderIdentifier(Base):
    """Multiple identifiers per bidder — e.g. multiple GSTINs for different states."""
    __tablename__ = "bidder_identifiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bidder_id: Mapped[str] = mapped_column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    identifier_type: Mapped[str] = mapped_column(String(50))  # PAN | GSTIN | CIN | UDYAM | EMAIL | PHONE | DOMAIN
    identifier_value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    state: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bidder: Mapped["Bidder"] = relationship("Bidder", back_populates="identifiers")
