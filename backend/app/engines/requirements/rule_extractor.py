"""
Deterministic Requirement Rule Extractor.

Extracts tender requirements using high-precision keyword patterns and regex rules.
"""
import re
import structlog
from typing import List, Dict, Any, Optional

from app.engines.requirements.schemas import TenderRequirementContract, RequirementType, RequirementOperator
from app.engines.requirements.normalizer import requirement_normalizer

logger = structlog.get_logger(__name__)

class RequirementRuleExtractor:
    def extract_requirements(self, text: str, page_number: int) -> List[TenderRequirementContract]:
        reqs: List[TenderRequirementContract] = []
        if not text:
            return reqs

        lines = text.split("\n")
        req_count = 1

        for line in lines:
            line_str = line.strip()
            if len(line_str) < 15:
                continue

            line_lower = line_str.lower()
            if any(k in line_lower for k in ("turnover", "experience", "gst", "pan", "mca", "udyam", "emd", "eligibility", "qualification")):
                req_type, op, req_val, unit = requirement_normalizer.normalize_statement(line_str)
                req_id = f"REQ_{req_type.value}_{req_count:03d}"
                req_count += 1

                reqs.append(TenderRequirementContract(
                    requirement_id=req_id,
                    requirement_type=req_type,
                    name=f"Tender Requirement - {req_type.value}",
                    description=line_str,
                    operator=op,
                    required_value=req_val,
                    unit=unit,
                    mandatory=True,
                    source_page=page_number,
                    source_excerpt=line_str[:200],
                    confidence=0.95,
                    extraction_method="REGEX",
                ))

        return reqs

requirement_rule_extractor = RequirementRuleExtractor()
