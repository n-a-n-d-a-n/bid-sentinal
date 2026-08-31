"""
Graph Relationship Factory.

Standardizes Graph Relationship Types:
BIDDER_SUBMITTED_BID, BIDDER_HAS_PAN, BIDDER_HAS_GSTIN, BIDDER_HAS_CIN, BIDDER_HAS_UDYAM,
BIDDER_HAS_ADDRESS, BIDDER_HAS_BANK_ACCOUNT, BIDDER_HAS_DIRECTOR, PERSON_DIRECTOR_OF,
BIDDER_WON_TENDER, DOCUMENT_SUPPORTS_BIDDER, ENTITY_MATCH, ENTITY_POSSIBLE_MATCH
"""
import uuid
from typing import Dict, Any, Optional

class GraphRelationshipFactory:
    @staticmethod
    def create_relationship_dict(
        source_id: str,
        target_id: str,
        relationship_type: str,
        confidence: float = 1.0,
        source_document: Optional[str] = None,
        source_page: Optional[int] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type.upper(),
            "confidence": confidence,
            "source_document": source_document,
            "source_page": source_page,
            "evidence": evidence or {},
        }

graph_relationship_factory = GraphRelationshipFactory()
