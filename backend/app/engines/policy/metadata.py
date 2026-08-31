"""
Policy Metadata & Versioning Definitions.

Policy Version Statuses:
- ACTIVE: Current authoritative version.
- SUPERSEDED: Legacy version replaced by newer policy.
- DRAFT: Proposed policy update.
- ARCHIVED: Retained for audit history.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class PolicyVersionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"

@dataclass
class PolicySourceMetadata:
    source_code: str
    authority: str
    document_name: str
    document_type: str  # GFR | GEM_MANUAL | MANUAL | CIRCULAR | NOTIFICATION
    official_url: Optional[str] = None
    current_version: str = "2017"
    status: PolicyVersionStatus = PolicyVersionStatus.ACTIVE
    sector: Optional[str] = "PUBLIC_PROCUREMENT"
