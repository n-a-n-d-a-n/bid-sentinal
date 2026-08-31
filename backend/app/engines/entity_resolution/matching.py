"""
Entity Matching Algorithms.

Combines:
1. Exact Identifier Match (PAN, GSTIN, CIN, Udyam) -> Score 1.0
2. Normalized Exact String Match -> Score 0.95
3. Fuzzy Ratio Matching (rapidfuzz / token set ratio) -> Score 0.0 to 0.90
"""
from typing import Dict, Any, Tuple, Optional
import structlog

from app.engines.entity_resolution.normalizer import entity_normalizer

logger = structlog.get_logger(__name__)

class EntityMatcher:
    @staticmethod
    def match_entities(
        entity_a: Dict[str, Any],
        entity_b: Dict[str, Any],
    ) -> Tuple[str, float, str, Dict[str, Any]]:
        """
        Matches entity_a against entity_b.
        Returns: (match_status, confidence_score, matching_method, evidence_details)
        Status values: MATCHED | POSSIBLE_MATCH | NO_MATCH | INSUFFICIENT_DATA
        """
        pan_a = entity_normalizer.normalize_identifier(entity_a.get("pan"))
        pan_b = entity_normalizer.normalize_identifier(entity_b.get("pan"))

        gstin_a = entity_normalizer.normalize_identifier(entity_a.get("gstin"))
        gstin_b = entity_normalizer.normalize_identifier(entity_b.get("gstin"))

        cin_a = entity_normalizer.normalize_identifier(entity_a.get("cin"))
        cin_b = entity_normalizer.normalize_identifier(entity_b.get("cin"))

        udyam_a = entity_normalizer.normalize_identifier(entity_a.get("udyam_number"))
        udyam_b = entity_normalizer.normalize_identifier(entity_b.get("udyam_number"))

        # 1. Strong Deterministic Identifier Matching
        if pan_a and pan_b and pan_a == pan_b:
            return "MATCHED", 1.0, "EXACT_PAN_MATCH", {"matched_field": "pan", "value": pan_a}

        if gstin_a and gstin_b and gstin_a == gstin_b:
            return "MATCHED", 1.0, "EXACT_GSTIN_MATCH", {"matched_field": "gstin", "value": gstin_a}

        if cin_a and cin_b and cin_a == cin_b:
            return "MATCHED", 1.0, "EXACT_CIN_MATCH", {"matched_field": "cin", "value": cin_a}

        if udyam_a and udyam_b and udyam_a == udyam_b:
            return "MATCHED", 1.0, "EXACT_UDYAM_MATCH", {"matched_field": "udyam_number", "value": udyam_a}

        # 2. Normalized Name Matching
        name_a = entity_normalizer.normalize_company_name(entity_a.get("name") or entity_a.get("canonical_name"))
        name_b = entity_normalizer.normalize_company_name(entity_b.get("name") or entity_b.get("canonical_name"))

        if not name_a or not name_b:
            return "INSUFFICIENT_DATA", 0.0, "NO_NAME_PROVIDED", {}

        if name_a == name_b:
            return "MATCHED", 0.95, "NORMALIZED_NAME_MATCH", {"matched_name": name_a}

        # 3. Fuzzy Matching
        fuzzy_score = 0.0
        try:
            from rapidfuzz import fuzz
            fuzzy_score = fuzz.token_set_ratio(name_a, name_b) / 100.0
        except ImportError:
            # Fallback simple overlap ratio
            tokens_a = set(name_a.split())
            tokens_b = set(name_b.split())
            if tokens_a and tokens_b:
                intersection = tokens_a.intersection(tokens_b)
                fuzzy_score = len(intersection) / max(len(tokens_a), len(tokens_b))

        if fuzzy_score >= 0.85:
            # High fuzzy similarity is POSSIBLE_MATCH, not definitive MATCHED unless verified
            return "POSSIBLE_MATCH", round(fuzzy_score, 2), "FUZZY_NAME_MATCH", {
                "name_a": name_a, "name_b": name_b, "similarity": round(fuzzy_score, 2)
            }

        return "NO_MATCH", round(fuzzy_score, 2), "LOW_SIMILARITY", {
            "name_a": name_a, "name_b": name_b, "similarity": round(fuzzy_score, 2)
        }

entity_matcher = EntityMatcher()
