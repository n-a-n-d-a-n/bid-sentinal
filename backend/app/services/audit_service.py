"""
Audit Service — append-only event logging.

Every significant action must be recorded through this service.
The audit ledger is append-only — events are never deleted or modified.
"""
from datetime import UTC, datetime
from typing import Any, Dict, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.misc import AuditRepository

logger = structlog.get_logger(__name__)

# Canonical action names
class AuditAction:
    # Auth
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    # Tenders
    TENDER_CREATE = "TENDER_CREATE"
    TENDER_UPDATE = "TENDER_UPDATE"
    TENDER_DOCUMENT_UPLOAD = "TENDER_DOCUMENT_UPLOAD"
    REQUIREMENT_CREATE = "REQUIREMENT_CREATE"
    REQUIREMENT_APPROVE = "REQUIREMENT_APPROVE"
    REQUIREMENT_UPDATE = "REQUIREMENT_UPDATE"
    # Bids
    BID_CREATE = "BID_CREATE"
    BID_UPDATE = "BID_UPDATE"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    DOCUMENT_DELETE = "DOCUMENT_DELETE"
    # Analysis
    VERIFICATION_REQUEST = "VERIFICATION_REQUEST"
    VERIFICATION_RESULT = "VERIFICATION_RESULT"
    RULE_EVALUATION = "RULE_EVALUATION"
    RISK_CALCULATION = "RISK_CALCULATION"
    BID_ANALYSIS_START = "BID_ANALYSIS_START"
    BID_ANALYSIS_COMPLETE = "BID_ANALYSIS_COMPLETE"
    # Decisions
    OFFICER_REVIEW = "OFFICER_REVIEW"
    OFFICER_DECISION = "OFFICER_DECISION"
    # Admin
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DEACTIVATE = "USER_DEACTIVATE"
    DEMO_SCENARIO_LOAD = "DEMO_SCENARIO_LOAD"
    # Security
    SECURITY_VALIDATION_FAIL = "SECURITY_VALIDATION_FAIL"
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
    # System
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SEED = "SYSTEM_SEED"


class AuditCategory:
    AUTH = "AUTH"
    DOCUMENT = "DOCUMENT"
    VERIFICATION = "VERIFICATION"
    COMPLIANCE = "COMPLIANCE"
    DECISION = "DECISION"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
    AI = "AI"
    SECURITY = "SECURITY"


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log(
        self,
        action: str,
        action_category: str,
        *,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        bid_id: Optional[str] = None,
        tender_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        change_summary: Optional[str] = None,
        document_hash: Optional[str] = None,
        rule_version: Optional[str] = None,
        model_version: Optional[str] = None,
        source: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log an audit event. This is the ONLY way to write audit events."""
        from app.models.audit import AuditEvent
        event = await self.repo.log(
            action=action,
            action_category=action_category,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            entity_type=entity_type,
            entity_id=entity_id,
            bid_id=bid_id,
            tender_id=tender_id,
            old_value=old_value,
            new_value=new_value,
            change_summary=change_summary,
            document_hash=document_hash,
            rule_version=rule_version,
            model_version=model_version,
            source=source or "API",
            request_id=request_id,
            ip_address=ip_address,
            metadata_=metadata,
            timestamp=datetime.now(UTC),
        )
        logger.info(
            "audit_event",
            action=action,
            category=action_category,
            entity=entity_id,
            user=user_email or user_id,
        )
        return event
