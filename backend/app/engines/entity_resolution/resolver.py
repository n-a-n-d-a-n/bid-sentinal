"""
Entity Resolver Service.

Resolves extracted bidder identity against database Bidders & BidderIdentifiers.
Enforces Safety Rules:
- LOW CONFIDENCE ≠ MATCH
- UNKNOWN ≠ MATCH
- UNAVAILABLE ≠ MATCH
"""
import structlog
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bidder import Bidder, BidderIdentifier
from app.repositories.bidders import BidderRepository
from app.engines.entity_resolution.normalizer import entity_normalizer
from app.engines.entity_resolution.matching import entity_matcher

logger = structlog.get_logger(__name__)

class EntityResolverService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BidderRepository(db)

    async def resolve_bidder(
        self,
        extracted_fields: Dict[str, str],
    ) -> Tuple[str, Optional[Bidder], float, str, Dict[str, Any]]:
        """
        Resolves bidder identity from extracted fields dictionary.
        Returns: (match_status, bidder_model, confidence_score, method, evidence)
        """
        pan = extracted_fields.get("pan")
        gstin = extracted_fields.get("gstin")
        cin = extracted_fields.get("cin")
        udyam = extracted_fields.get("udyam_number")
        name = extracted_fields.get("legal_name") or extracted_fields.get("canonical_name")

        candidate_data = {
            "name": name,
            "pan": pan,
            "gstin": gstin,
            "cin": cin,
            "udyam_number": udyam,
        }

        # 1. Search by PAN if available
        if pan:
            existing = await self.repo.get_by_pan(pan)
            if existing:
                return "MATCHED", existing, 1.0, "EXACT_PAN_MATCH", {"matched_field": "pan", "pan": pan}

        # 2. Search by GSTIN if available
        if gstin:
            existing = await self.repo.get_by_gstin(gstin)
            if existing:
                return "MATCHED", existing, 1.0, "EXACT_GSTIN_MATCH", {"matched_field": "gstin", "gstin": gstin}

        # 3. Search by CIN if available
        if cin:
            existing = await self.repo.get_by_cin(cin)
            if existing:
                return "MATCHED", existing, 1.0, "EXACT_CIN_MATCH", {"matched_field": "cin", "cin": cin}

        # 4. Search by Name
        if name:
            bidders = await self.repo.search(name, limit=10)
            best_match: Optional[Bidder] = None
            best_status = "NO_MATCH"
            best_score = 0.0
            best_method = "NONE"
            best_evidence = {}

            for bidder in bidders:
                b_dict = {
                    "name": bidder.canonical_name,
                    "pan": bidder.pan,
                    "gstin": bidder.gstin,
                    "cin": bidder.cin,
                    "udyam_number": bidder.udyam_number,
                }
                status, score, method, evidence = entity_matcher.match_entities(candidate_data, b_dict)
                if score > best_score:
                    best_score = score
                    best_status = status
                    best_match = bidder
                    best_method = method
                    best_evidence = evidence

            if best_match and best_status == "MATCHED":
                return "MATCHED", best_match, best_score, best_method, best_evidence
            elif best_match and best_status == "POSSIBLE_MATCH":
                return "POSSIBLE_MATCH", best_match, best_score, best_method, best_evidence

        return "NO_MATCH", None, 0.0, "NO_IDENTIFIER_OR_NAME_MATCH", {}
