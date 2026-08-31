"""
Entity Normalizer.

Standardizes company names, addresses, and identifiers for deterministic matching.
Strips corporate suffixes (Pvt Ltd, Private Limited, Corp, Inc, LLP, Co.), punctuation, and extra whitespace.
"""
import re
import unicodedata
from typing import Optional

SUFFIXES = [
    r"\bprivate\s+limited\b",
    r"\bpvt\.?\s*ltd\.?\b",
    r"\blimited\b",
    r"\bltd\.?\b",
    r"\bcorporation\b",
    r"\bcorp\.?\b",
    r"\bincorporated\b",
    r"\binc\.?\b",
    r"\bllp\b",
    r"\bcompany\b",
    r"\bco\.?\b",
    r"\benterprises\b",
    r"\bsolutions\b",
    r"\bservices\b",
    r"\btechnologies\b",
]

class EntityNormalizer:
    @staticmethod
    def normalize_company_name(name: str) -> str:
        if not name:
            return ""

        # Lowercase & Unicode normalization
        clean = unicodedata.normalize("NFKC", name.lower())

        # Remove corporate suffixes
        for pattern in SUFFIXES:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

        # Remove special characters
        clean = re.sub(r"[^a-z0-9\s]", " ", clean)

        # Collapse whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @staticmethod
    def normalize_identifier(identifier: Optional[str]) -> str:
        if not identifier:
            return ""
        return re.sub(r"[^A-Za-z0-9]", "", identifier.strip().upper())

entity_normalizer = EntityNormalizer()
