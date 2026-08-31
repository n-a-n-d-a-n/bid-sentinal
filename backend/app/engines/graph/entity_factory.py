"""
Graph Entity Factory.

Standardizes Graph Entity Types:
BIDDER, ORGANIZATION, PERSON, TENDER, BID, DOCUMENT, PAN, GSTIN, CIN, UDYAM, ADDRESS, BANK_ACCOUNT, DIRECTOR
"""
import uuid
from typing import Dict, Any, Optional

class GraphEntityFactory:
    @staticmethod
    def create_entity_dict(
        canonical_name: str,
        entity_type: str,
        source: str = "EXTRACTED_DOCUMENTS",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "canonical_name": canonical_name.strip(),
            "entity_type": entity_type.upper(),
            "source": source,
            "confidence": confidence,
            "metadata": metadata or {},
        }

graph_entity_factory = GraphEntityFactory()
