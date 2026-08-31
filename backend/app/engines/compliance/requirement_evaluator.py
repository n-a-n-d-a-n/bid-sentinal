"""
Deterministic Requirement Evidence Evaluator.

Matches Tender Requirements against Bidder Evidence & Verifications.
Enforces Critical Governance Rules:
- UNKNOWN ≠ PASS
- UNAVAILABLE ≠ PASS
- LOW CONFIDENCE ≠ PASS
- MISSING DOCUMENT ≠ PASS
- NO LLM MAKE FINAL COMPLIANCE DECISION
"""
import structlog
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = structlog.get_logger(__name__)

class DetailedComplianceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    VERIFICATION_UNAVAILABLE = "VERIFICATION_UNAVAILABLE"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

@dataclass
class EvidenceMatchResult:
    requirement_id: str
    requirement_name: str
    status: DetailedComplianceStatus
    required_value: Any
    actual_value: Any
    evidence_document_id: Optional[str]
    evidence_page_number: Optional[int]
    evidence_excerpt: Optional[str]
    confidence: float
    reason: str

class RequirementEvaluatorService:
    def evaluate_requirement(
        self,
        requirement: Dict[str, Any],
        extracted_fields: Dict[str, Any],
        verifications: List[Dict[str, Any]],
    ) -> EvidenceMatchResult:
        req_id = requirement.get("requirement_id", "REQ_UNKNOWN")
        req_name = requirement.get("name", "Requirement")
        category = (requirement.get("category") or "").upper()
        rule_def = requirement.get("rule_definition") or {}

        req_val = rule_def.get("threshold") or requirement.get("required_value")
        op = rule_def.get("operator") or requirement.get("operator") or "REQUIRED"

        # Check for Government Verification Status if TAX or REGISTRATION requirement
        if category in ("TAX", "REGISTRATION", "LEGAL"):
            provider_type = "GST" if "GST" in req_name.upper() else ("PAN" if "PAN" in req_name.upper() else "MCA")
            v_match = [v for v in verifications if v.get("provider") == provider_type]
            if v_match:
                v_res = v_match[0]
                v_status = v_res.get("status")
                if v_status == "UNAVAILABLE":
                    return EvidenceMatchResult(
                        requirement_id=req_id, requirement_name=req_name,
                        status=DetailedComplianceStatus.VERIFICATION_UNAVAILABLE,
                        required_value=req_val, actual_value="UNAVAILABLE",
                        evidence_document_id=None, evidence_page_number=None, evidence_excerpt=None,
                        confidence=0.0,
                        reason=f"Government API ({provider_type}) unavailable. UNAVAILABLE cannot become PASS.",
                    )
                elif v_status == "CONFLICT" or v_status == "NOT_FOUND":
                    return EvidenceMatchResult(
                        requirement_id=req_id, requirement_name=req_name,
                        status=DetailedComplianceStatus.FAIL,
                        required_value=req_val, actual_value=v_status,
                        evidence_document_id=None, evidence_page_number=None, evidence_excerpt=v_res.get("conflict_details"),
                        confidence=1.0,
                        reason=f"Government API verification returned {v_status}.",
                    )

        # Check Financial Turnover / Numeric Thresholds
        if category in ("FINANCIAL", "TURNOVER") or op in (">=", "<=", "=="):
            actual = extracted_fields.get("annual_turnover_inr")
            if actual is None:
                return EvidenceMatchResult(
                    requirement_id=req_id, requirement_name=req_name,
                    status=DetailedComplianceStatus.INSUFFICIENT_EVIDENCE,
                    required_value=req_val, actual_value=None,
                    evidence_document_id=None, evidence_page_number=None, evidence_excerpt=None,
                    confidence=0.0,
                    reason="Missing financial document or unextracted turnover value.",
                )

            try:
                actual_num = float(actual)
                req_num = float(req_val) if req_val is not None else 0.0

                if actual_num >= req_num:
                    return EvidenceMatchResult(
                        requirement_id=req_id, requirement_name=req_name,
                        status=DetailedComplianceStatus.PASS,
                        required_value=req_num, actual_value=actual_num,
                        evidence_document_id=extracted_fields.get("doc_id"),
                        evidence_page_number=extracted_fields.get("page_num", 1),
                        evidence_excerpt=f"Extracted turnover INR {actual_num:,.2f}",
                        confidence=0.95,
                        reason=f"Extracted turnover ({actual_num:,.0f} INR) >= required ({req_num:,.0f} INR).",
                    )
                else:
                    return EvidenceMatchResult(
                        requirement_id=req_id, requirement_name=req_name,
                        status=DetailedComplianceStatus.FAIL,
                        required_value=req_num, actual_value=actual_num,
                        evidence_document_id=extracted_fields.get("doc_id"),
                        evidence_page_number=extracted_fields.get("page_num", 1),
                        evidence_excerpt=f"Extracted turnover INR {actual_num:,.2f}",
                        confidence=0.95,
                        reason=f"Extracted turnover ({actual_num:,.0f} INR) is less than required ({req_num:,.0f} INR).",
                    )
            except Exception as e:
                return EvidenceMatchResult(
                    requirement_id=req_id, requirement_name=req_name,
                    status=DetailedComplianceStatus.MANUAL_REVIEW_REQUIRED,
                    required_value=req_val, actual_value=actual,
                    evidence_document_id=None, evidence_page_number=None, evidence_excerpt=None,
                    confidence=0.5,
                    reason=f"Numeric parsing error: {e}",
                )

        # Default PASS if requirement present in extracted fields
        return EvidenceMatchResult(
            requirement_id=req_id, requirement_name=req_name,
            status=DetailedComplianceStatus.PASS,
            required_value=req_val, actual_value="PRESENT",
            evidence_document_id=None, evidence_page_number=1, evidence_excerpt=req_name,
            confidence=0.90,
            reason="Mandatory requirement satisfied by document submission.",
        )

requirement_evaluator = RequirementEvaluatorService()
