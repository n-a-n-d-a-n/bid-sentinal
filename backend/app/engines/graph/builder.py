"""
Graph Builder & NetworkX Pipeline.

Populates GraphEntity and GraphRelationship DB models from bids, bidders, documents, and extractions.
Provides automatic cross-referencing between bidders upon document processing or onboarding.
Exports network to NetworkX Graph instance for analytics.
"""
import structlog
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple, Set
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.graph import GraphEntity, GraphRelationship
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.document import Document, ExtractedField
from app.engines.graph.entity_factory import graph_entity_factory
from app.engines.graph.relationship_factory import graph_relationship_factory

logger = structlog.get_logger(__name__)


class GraphBuilderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_entity(
        self,
        node_id: str,
        entity_type: str,
        label: str,
        entity_ref_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> GraphEntity:
        res = await self.db.execute(select(GraphEntity).where(GraphEntity.node_id == node_id))
        entity = res.scalar_one_or_none()
        if not entity:
            entity = GraphEntity(
                node_id=node_id,
                entity_type=entity_type.upper(),
                entity_ref_id=entity_ref_id,
                label=label,
                properties=properties or {},
                risk_score=1.0,
            )
            self.db.add(entity)
            await self.db.flush()
        return entity

    async def create_relationship_if_not_exists(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        confidence: float = 1.0,
        evidence: Optional[str] = None,
        source: str = "AUTO_DETECTION",
    ) -> Optional[GraphRelationship]:
        res = await self.db.execute(
            select(GraphRelationship).where(
                GraphRelationship.source_node_id == source_node_id,
                GraphRelationship.target_node_id == target_node_id,
                GraphRelationship.relationship_type == relationship_type.upper(),
            )
        )
        existing = res.scalar_one_or_none()
        if existing:
            return None

        rel = GraphRelationship(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type.upper(),
            confidence=confidence,
            evidence=evidence,
            source=source,
        )
        self.db.add(rel)
        await self.db.flush()
        return rel

    async def auto_cross_reference_bidder(self, bidder_id: str, document_id: Optional[str] = None) -> List[GraphRelationship]:
        """
        Automatically cross-references a bidder's profile and document extractions
        against all existing bidders in the DB.
        Inserts GraphEntity and GraphRelationship rows upon detecting shared attributes.
        Triggers risk recalculation for active bids involving the affected bidders.
        """
        logger.info("auto_cross_reference_start", bidder_id=bidder_id, document_id=document_id)

        res = await self.db.execute(select(Bidder).where(Bidder.id == bidder_id))
        bidder: Optional[Bidder] = res.scalar_one_or_none()
        if not bidder:
            return []

        # 1. Ensure Bidder Entity
        bidder_node_id = f"bidder:{bidder.id}"
        await self.get_or_create_entity(
            node_id=bidder_node_id,
            entity_type="BIDDER",
            label=bidder.canonical_name,
            entity_ref_id=bidder.id,
            properties={"pan": bidder.pan, "gstin": bidder.gstin, "state": bidder.state},
        )

        created_rels: List[GraphRelationship] = []
        affected_bidder_ids: Set[str] = {bidder.id}

        # Gather attributes to match
        attributes_to_check: List[Tuple[str, str, str]] = []  # (attr_type, raw_val, norm_val)

        if bidder.pan:
            attributes_to_check.append(("PAN", bidder.pan, bidder.pan.upper().strip()))
        if bidder.gstin:
            attributes_to_check.append(("GSTIN", bidder.gstin, bidder.gstin.upper().strip()))
        if bidder.registered_address:
            attributes_to_check.append(("ADDRESS", bidder.registered_address, bidder.registered_address.lower().strip()))

        # Gather extracted fields from documents for this bidder
        doc_subquery = select(Document.id).where(
            or_(
                Document.entity_id == bidder.id,
                Document.entity_id.in_(select(Bid.id).where(Bid.bidder_id == bidder.id)),
            )
        )
        fields_res = await self.db.execute(select(ExtractedField).where(ExtractedField.document_id.in_(doc_subquery)))
        extracted_fields = fields_res.scalars().all()

        for ef in extracted_fields:
            fn = (ef.field_name or "").lower().strip()
            fv = (ef.field_value or "").strip()
            if not fv:
                continue

            if fn in ("director", "director_name", "authorized_signatory"):
                attributes_to_check.append(("DIRECTOR", fv, fv.lower()))
            elif fn in ("address", "registered_address"):
                attributes_to_check.append(("ADDRESS", fv, fv.lower()))
            elif fn in ("bank_account", "bank_account_number", "account_number"):
                attributes_to_check.append(("BANK_ACCOUNT", fv, fv.strip()))
            elif fn in ("pan", "pan_number"):
                attributes_to_check.append(("PAN", fv, fv.upper()))
            elif fn in ("gstin", "gst_number"):
                attributes_to_check.append(("GSTIN", fv, fv.upper()))

        # Perform cross-referencing against all other bidders
        other_bidders_res = await self.db.execute(select(Bidder).where(Bidder.id != bidder.id))
        other_bidders = other_bidders_res.scalars().all()

        for other in other_bidders:
            other_node_id = f"bidder:{other.id}"
            
            # Gather other bidder attributes
            other_attrs: List[Tuple[str, str, str]] = []
            if other.pan:
                other_attrs.append(("PAN", other.pan, other.pan.upper().strip()))
            if other.gstin:
                other_attrs.append(("GSTIN", other.gstin, other.gstin.upper().strip()))
            if other.registered_address:
                other_attrs.append(("ADDRESS", other.registered_address, other.registered_address.lower().strip()))

            other_doc_subquery = select(Document.id).where(
                or_(
                    Document.entity_id == other.id,
                    Document.entity_id.in_(select(Bid.id).where(Bid.bidder_id == other.id)),
                )
            )
            other_fields_res = await self.db.execute(select(ExtractedField).where(ExtractedField.document_id.in_(other_doc_subquery)))
            for o_ef in other_fields_res.scalars().all():
                o_fn = (o_ef.field_name or "").lower().strip()
                o_fv = (o_ef.field_value or "").strip()
                if not o_fv:
                    continue
                if o_fn in ("director", "director_name", "authorized_signatory"):
                    other_attrs.append(("DIRECTOR", o_fv, o_fv.lower()))
                elif o_fn in ("address", "registered_address"):
                    other_attrs.append(("ADDRESS", o_fv, o_fv.lower()))
                elif o_fn in ("bank_account", "bank_account_number", "account_number"):
                    other_attrs.append(("BANK_ACCOUNT", o_fv, o_fv.strip()))
                elif o_fn in ("pan", "pan_number"):
                    other_attrs.append(("PAN", o_fv, o_fv.upper()))
                elif o_fn in ("gstin", "gst_number"):
                    other_attrs.append(("GSTIN", o_fv, o_fv.upper()))

            # Check matches between bidder and other
            for a_type, raw_val, norm_val in attributes_to_check:
                for o_type, o_raw_val, o_norm_val in other_attrs:
                    if a_type == o_type and norm_val == o_norm_val and norm_val:
                        # Shared attribute match detected!
                        logger.info(
                            "shared_attribute_detected",
                            attr_type=a_type,
                            val=raw_val,
                            bidder_1=bidder.canonical_name,
                            bidder_2=other.canonical_name,
                        )

                        # Ensure other bidder node
                        await self.get_or_create_entity(
                            node_id=other_node_id,
                            entity_type="BIDDER",
                            label=other.canonical_name,
                            entity_ref_id=other.id,
                        )

                        # Attribute Node
                        attr_node_id = f"{a_type.lower()}:{norm_val}"
                        await self.get_or_create_entity(
                            node_id=attr_node_id,
                            entity_type=a_type,
                            label=raw_val,
                        )

                        # Edges: Bidder -> Attr, Other -> Attr
                        r1 = await self.create_relationship_if_not_exists(
                            source_node_id=bidder_node_id,
                            target_node_id=attr_node_id,
                            relationship_type=f"BIDDER_HAS_{a_type}",
                            evidence=f"Extracted matching {a_type} '{raw_val}'",
                        )
                        r2 = await self.create_relationship_if_not_exists(
                            source_node_id=other_node_id,
                            target_node_id=attr_node_id,
                            relationship_type=f"BIDDER_HAS_{a_type}",
                            evidence=f"Extracted matching {a_type} '{raw_val}'",
                        )
                        # Direct SHARED Edge between bidders
                        r3 = await self.create_relationship_if_not_exists(
                            source_node_id=bidder_node_id,
                            target_node_id=other_node_id,
                            relationship_type=f"SHARES_{a_type}",
                            evidence=f"Both bidders share {a_type} '{raw_val}'",
                        )

                        for r in (r1, r2, r3):
                            if r:
                                created_rels.append(r)

                        affected_bidder_ids.add(other.id)

        await self.db.flush()

        # Trigger automatic risk recalculation for active bids involving affected bidders (Item 4 Hook)
        if created_rels:
            from app.services.risk_service import recalculate_risk_for_bidder_bids
            for b_id in affected_bidder_ids:
                await recalculate_risk_for_bidder_bids(self.db, b_id, source="AUTOMATED_GRAPH_DETECTION")

        logger.info(
            "auto_cross_reference_complete",
            bidder_id=bidder_id,
            new_edges_count=len(created_rels),
            affected_bidders_count=len(affected_bidder_ids),
        )
        return created_rels

    async def build_graph_for_bidder(self, bidder_id: str) -> nx.Graph:
        """
        Populates DB graph tables for bidder and builds in-memory NetworkX Graph.
        """
        res = await self.db.execute(select(Bidder).where(Bidder.id == bidder_id))
        bidder: Optional[Bidder] = res.scalar_one_or_none()
        if not bidder:
            return nx.Graph()

        bidder_node_id = f"bidder:{bidder.id}"
        await self.get_or_create_entity(
            node_id=bidder_node_id,
            entity_type="BIDDER",
            label=bidder.canonical_name,
            entity_ref_id=bidder.id,
            properties={"pan": bidder.pan, "gstin": bidder.gstin, "state": bidder.state},
        )

        if bidder.pan:
            pan_node_id = f"pan:{bidder.pan.upper()}"
            await self.get_or_create_entity(node_id=pan_node_id, entity_type="PAN", label=bidder.pan)
            await self.create_relationship_if_not_exists(bidder_node_id, pan_node_id, "BIDDER_HAS_PAN")

        if bidder.gstin:
            gst_node_id = f"gstin:{bidder.gstin.upper()}"
            await self.get_or_create_entity(node_id=gst_node_id, entity_type="GSTIN", label=bidder.gstin)
            await self.create_relationship_if_not_exists(bidder_node_id, gst_node_id, "BIDDER_HAS_GSTIN")

        if bidder.registered_address:
            addr_node_id = f"address:{bidder.registered_address.lower()[:100]}"
            await self.get_or_create_entity(node_id=addr_node_id, entity_type="ADDRESS", label=bidder.registered_address)
            await self.create_relationship_if_not_exists(bidder_node_id, addr_node_id, "BIDDER_HAS_ADDRESS")

        # Run auto cross referencing
        await self.auto_cross_reference_bidder(bidder_id)
        await self.db.commit()

        return await self.export_to_networkx()

    async def export_to_networkx(self) -> nx.Graph:
        G = nx.Graph()
        entities_res = await self.db.execute(select(GraphEntity))
        entities = entities_res.scalars().all()
        for e in entities:
            G.add_node(e.node_id, label=e.label or e.node_id, type=e.entity_type, confidence=e.risk_score or 1.0)

        rels_res = await self.db.execute(select(GraphRelationship))
        rels = rels_res.scalars().all()
        for r in rels:
            G.add_edge(r.source_node_id, r.target_node_id, relationship=r.relationship_type, confidence=r.confidence)

        return G


graph_builder = GraphBuilderService
