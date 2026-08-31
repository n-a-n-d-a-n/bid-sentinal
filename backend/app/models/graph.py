"""Graph entity and relationship models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GraphEntity(Base):
    __tablename__ = "graph_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # COMPANY | DIRECTOR | PAN | GSTIN | CIN | ADDRESS | PHONE | EMAIL |
    # IP | DEVICE | BID | TENDER | BANK | OEM | DOCUMENT
    entity_ref_id: Mapped[str | None] = mapped_column(String(36), index=True)  # FK to actual entity
    label: Mapped[str] = mapped_column(String(500))
    properties: Mapped[dict | None] = mapped_column(JSON)
    risk_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    outgoing_edges: Mapped[list["GraphRelationship"]] = relationship(
        "GraphRelationship",
        back_populates="source_entity",
        foreign_keys="[GraphRelationship.source_node_id]",
    )
    incoming_edges: Mapped[list["GraphRelationship"]] = relationship(
        "GraphRelationship",
        back_populates="target_entity",
        foreign_keys="[GraphRelationship.target_node_id]",
    )


class GraphRelationship(Base):
    __tablename__ = "graph_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id: Mapped[str] = mapped_column(String(100), ForeignKey("graph_entities.node_id"), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(String(100), ForeignKey("graph_entities.node_id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # DIRECTOR_OF | HAS_GST | HAS_PAN | REGISTERED_AT | SUBMITTED_BID |
    # PARTICIPATED_IN | SHARES_ADDRESS | SHARES_PHONE | SHARES_EMAIL |
    # SHARES_IP | AUTHORISED_BY | USES_BANK
    properties: Mapped[dict | None] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))  # data source
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    source_entity: Mapped["GraphEntity"] = relationship(
        "GraphEntity", back_populates="outgoing_edges", foreign_keys=[source_node_id]
    )
    target_entity: Mapped["GraphEntity"] = relationship(
        "GraphEntity", back_populates="incoming_edges", foreign_keys=[target_node_id]
    )
