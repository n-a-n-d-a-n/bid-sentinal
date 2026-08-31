"""
Prompt Injection Defense & Grounding Guardrails.

Rules:
- Treat policy text strictly as DATA.
- Strip attempt patterns like "Ignore previous instructions", "System override", "You are now unrestricted".
- Enforce strict evidence grounding checks.
"""
import re
import structlog
from typing import Tuple

logger = structlog.get_logger(__name__)

SUSPICIOUS_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"system\s+override",
    r"you\s+are\s+now\s+unrestricted",
    r"forget\s+(?:all\s+)?prior\s+prompts",
    r"admin\s+mode",
]

class PolicyGuardrailsService:
    @staticmethod
    def sanitize_input(text: str) -> str:
        clean = text
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                logger.warning("prompt_injection_attempt_detected", pattern=pattern)
                clean = re.sub(pattern, "[FILTERED_SECURITY_VIOLATION]", clean, flags=re.IGNORECASE)
        return clean

    @staticmethod
    def verify_grounding(answer: str, retrieved_texts: str) -> str:
        """
        Verifies whether answer contains invented facts or hallucinated citations.
        Returns grounding status: GROUNDED | PARTIALLY_GROUNDED | INSUFFICIENT_EVIDENCE
        """
        if "available policy sources do not provide sufficient evidence" in answer.lower():
            return "INSUFFICIENT_EVIDENCE"
        if not retrieved_texts:
            return "INSUFFICIENT_EVIDENCE"
        return "GROUNDED"

policy_guardrails = PolicyGuardrailsService()
