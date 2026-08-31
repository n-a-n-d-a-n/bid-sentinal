"""
Verification Engine — Government API adapter architecture.

Critical Governance Rule:
    UNAVAILABLE must NEVER become PASS.
    Mock adapters must be clearly labeled.
    Real adapters are pluggable replacements.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONFLICT = "CONFLICT"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    PENDING = "PENDING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class VerificationResult:
    source: str
    provider: str
    queried_identifier: str
    returned_identifier: Optional[str]
    status: VerificationStatus
    data: Optional[Dict[str, Any]]
    checked_at: datetime
    source_reference: Optional[str]
    authorization_context: str  # "LIVE_API" | "MOCK_SANDBOX" | "DEMO" | "MANUAL"
    confidence: float
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    conflict_details: Optional[str] = None
    is_mock: bool = True  # Default to True — must be explicitly set False for live
    is_demo: bool = True

    @property
    def is_unavailable(self) -> bool:
        return self.status == VerificationStatus.UNAVAILABLE

    @property
    def can_auto_pass(self) -> bool:
        """
        CRITICAL: UNAVAILABLE must NEVER auto-pass.
        Only VERIFIED can contribute to a compliance pass.
        """
        return self.status == VerificationStatus.VERIFIED


class VerificationProvider(ABC):
    """Base class for all government verification adapters."""

    provider_name: str = "UNKNOWN"
    is_mock: bool = True  # Subclasses must override

    @abstractmethod
    async def verify(self, identifier: str, **kwargs) -> VerificationResult:
        """Perform verification. Must handle all error cases."""
        ...

    def _make_unavailable(self, identifier: str, reason: str) -> VerificationResult:
        """Helper to create a properly labeled UNAVAILABLE result."""
        return VerificationResult(
            source=f"{self.provider_name}_ADAPTER",
            provider=self.provider_name,
            queried_identifier=identifier,
            returned_identifier=None,
            status=VerificationStatus.UNAVAILABLE,
            data=None,
            checked_at=datetime.now(UTC),
            source_reference=None,
            authorization_context="MOCK_SANDBOX" if self.is_mock else "LIVE_API",
            confidence=0.0,
            error_code="UNAVAILABLE",
            error_message=reason,
            is_mock=self.is_mock,
        )

    def _make_unauthorized(self, identifier: str) -> VerificationResult:
        return VerificationResult(
            source=f"{self.provider_name}_ADAPTER",
            provider=self.provider_name,
            queried_identifier=identifier,
            returned_identifier=None,
            status=VerificationStatus.UNAUTHORIZED,
            data=None,
            checked_at=datetime.now(UTC),
            source_reference=None,
            authorization_context="UNAUTHORIZED",
            confidence=0.0,
            error_code="UNAUTHORIZED",
            error_message="API credentials not configured. Verification requires authorization.",
            is_mock=self.is_mock,
        )
