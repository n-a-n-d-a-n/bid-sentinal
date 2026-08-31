"""
Deterministic Audit Payload Canonicalizer.

Ensures reproducible SHA-256 hash generation by canonicalizing dictionary keys and JSON strings.
"""
import json
from typing import Dict, Any

class AuditCanonicalizer:
    @staticmethod
    def canonicalize(payload: Dict[str, Any]) -> str:
        if payload is None:
            return ""
        # Sort keys recursively for deterministic string representation
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

audit_canonicalizer = AuditCanonicalizer()
