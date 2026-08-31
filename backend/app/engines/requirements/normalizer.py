"""
Tender Requirement Normalizer.

Converts natural-language procurement statements into canonical requirement definitions deterministically:
- "Average annual turnover should not be less than ₹5 crore" -> TURNOVER >= 50000000 INR
- "Bidder must have completed at least 3 similar projects" -> EXPERIENCE >= 3
- "GST registration is mandatory" -> TAX REQUIRED GST
- "Registration under Companies Act" -> REGISTRATION REQUIRED MCA_REGISTRATION
"""
import re
import structlog
from typing import Optional, Tuple, Any

from app.engines.requirements.schemas import RequirementType, RequirementOperator

logger = structlog.get_logger(__name__)

class RequirementNormalizerService:
    @staticmethod
    def normalize_statement(text: str) -> Tuple[RequirementType, RequirementOperator, Any, Optional[str]]:
        """
        Parses text and returns: (requirement_type, operator, required_value, unit)
        """
        text_lower = text.lower()

        # 1. Turnover Requirement
        turnover_match = re.search(r"turnover.*?(?:less|minimum|at least)?.*?₹?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|lakh|lakhs|lakh|inr)?", text_lower)
        if turnover_match or "turnover" in text_lower:
            val = 50000000.0  # Default 5 Cr if numeric parse fails
            if turnover_match and turnover_match.group(1):
                try:
                    raw_num = float(turnover_match.group(1).replace(",", ""))
                    unit = (turnover_match.group(2) or "").lower()
                    if "cr" in unit or "crore" in unit:
                        val = raw_num * 10_000_000
                    elif "lakh" in unit:
                        val = raw_num * 100_000
                    else:
                        val = raw_num
                except Exception:
                    pass
            return RequirementType.TURNOVER, RequirementOperator.GREATER_THAN_OR_EQUAL, val, "INR"

        # 2. Experience / Past Contract Count Requirement
        exp_match = re.search(r"(?:completed|executed|experience).*?(?:at least|minimum)?\s*(\d+)\s*(?:similar|projects|contracts|years)?", text_lower)
        if exp_match:
            try:
                count = float(exp_match.group(1))
                return RequirementType.EXPERIENCE, RequirementOperator.GREATER_THAN_OR_EQUAL, count, "COUNT"
            except Exception:
                pass

        # 3. GST Registration
        if "gst" in text_lower or "goods and services tax" in text_lower:
            return RequirementType.TAX, RequirementOperator.REQUIRED, "GST", None

        # 4. PAN Requirement
        if "pan" in text_lower or "permanent account number" in text_lower:
            return RequirementType.TAX, RequirementOperator.REQUIRED, "PAN", None

        # 5. MCA / Companies Act Registration
        if "companies act" in text_lower or "mca" in text_lower or "incorporation" in text_lower:
            return RequirementType.REGISTRATION, RequirementOperator.REQUIRED, "MCA_REGISTRATION", None

        # 6. MSME / Udyam
        if "udyam" in text_lower or "msme" in text_lower:
            return RequirementType.REGISTRATION, RequirementOperator.REQUIRED, "UDYAM_REGISTRATION", None

        # 7. EMD / Bid Security
        emd_match = re.search(r"(?:emd|earnest money|bid security).*?₹?\s*([\d,]+(?:\.\d+)?)", text_lower)
        if emd_match or "emd" in text_lower:
            emd_val = 100000.0
            if emd_match and emd_match.group(1):
                try:
                    emd_val = float(emd_match.group(1).replace(",", ""))
                except Exception:
                    pass
            return RequirementType.EMD, RequirementOperator.REQUIRED, emd_val, "INR"

        # Default fallback
        return RequirementType.ELIGIBILITY, RequirementOperator.REQUIRED, "MANDATORY_COMPLIANCE", None

requirement_normalizer = RequirementNormalizerService()
