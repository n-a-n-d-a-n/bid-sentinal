"""
Cryptographic Audit Event Hasher.

Computes SHA-256 event hash:
event_hash = SHA-256(action + entity_id + canonical_payload + timestamp_iso + previous_event_hash)
"""
import hashlib
from typing import Dict, Any, Optional
from app.engines.audit.canonicalizer import audit_canonicalizer

GENESIS_HASH = "GENESIS"

class AuditHasher:
    @staticmethod
    def calculate_event_hash(
        action: str,
        entity_id: Optional[str],
        payload: Dict[str, Any],
        timestamp_iso: str,
        previous_event_hash: str,
    ) -> str:
        canonical_str = audit_canonicalizer.canonicalize(payload)
        raw_to_hash = f"{action}|{entity_id or ''}|{canonical_str}|{timestamp_iso}|{previous_event_hash}"
        return hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()

audit_hasher = AuditHasher()
