"""
Document Classifier Service — Hybrid classification strategy.

Combines:
1. Filename & extension hints
2. Regex / Keyword signal matching
3. LLM classification fallback
4. Confidence scoring (0.0 - 1.0)
"""
import re
import structlog
from typing import Dict, Any, Tuple, Optional

logger = structlog.get_logger(__name__)

# Canonical document type constants
DOCUMENT_TYPES = [
    "TENDER_DOCUMENT",
    "TECHNICAL_SPECIFICATION",
    "FINANCIAL_DOCUMENT",
    "GST_DOCUMENT",
    "PAN_DOCUMENT",
    "UDYAM_DOCUMENT",
    "MCA_DOCUMENT",
    "BANK_DOCUMENT",
    "EXPERIENCE_CERTIFICATE",
    "EMD_DOCUMENT",
    "OTHER",
]

# Regex keyword signals
SIGNALS = {
    "GST_DOCUMENT": [
        r"goods\s+and\s+services\s+tax",
        r"gstin",
        r"form\s+gst\s+reg",
        r"registration\s+certificate.*gst",
    ],
    "PAN_DOCUMENT": [
        r"income\s+tax\s+department",
        r"permanent\s+account\s+number",
        r"govt\.\s+of\s+india.*pan",
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    ],
    "UDYAM_DOCUMENT": [
        r"udyam\s+registration\s+certificate",
        r"ministry\s+of\s+micro,\s+small\s+and\s+medium\s+enterprises",
        r"udyam-[a-z]{2}-\d{2}-\d{7}",
        r"msme\s+registration",
    ],
    "MCA_DOCUMENT": [
        r"certificate\s+of\s+incorporation",
        r"ministry\s+of\s+corporate\s+affairs",
        r"corporate\s+identity\s+number",
        r"\b[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b",
    ],
    "FINANCIAL_DOCUMENT": [
        r"audited\s+balance\s+sheet",
        r"profit\s+(?:and|&)\s+loss",
        r"chartered\s+accountant",
        r"annual\s+turnover",
        r"financial\s+statement",
        r"ca\s+certificate",
    ],
    "BANK_DOCUMENT": [
        r"bank\s+guarantee",
        r"solvency\s+certificate",
        r"ifsc\s+code",
        r"account\s+statement",
    ],
    "EXPERIENCE_CERTIFICATE": [
        r"completion\s+certificate",
        r"work\s+experience",
        r"performance\s+certificate",
        r"satisfactory\s+completion",
    ],
    "EMD_DOCUMENT": [
        r"earnest\s+money\s+deposit",
        r"emd\s+exemption",
        r"bid\_security",
        r"demand\s+draft.*emd",
    ],
    "TENDER_DOCUMENT": [
        r"notice\s+inviting\s+tender",
        r"gem\s+bid\s+number",
        r"terms\s+and\s+conditions",
        r"procurement\s+of",
        r"eligibility\s+criteria",
    ],
    "TECHNICAL_SPECIFICATION": [
        r"technical\s+specifications",
        r"bill\s+of\s+quantities",
        r"boq",
        r"scope\s+of\s+work",
    ],
}

class DocumentClassifierService:
    def classify(self, text: str, filename: str = "") -> Tuple[str, float, str]:
        """
        Classifies document based on text and filename signals.
        Returns: (document_type, confidence, classification_method)
        """
        fn_lower = filename.lower()
        text_lower = (text or "").lower()

        # 1. Filename heuristic matching
        if "gst" in fn_lower:
            return "GST_DOCUMENT", 0.90, "filename_rule"
        if "pan" in fn_lower:
            return "PAN_DOCUMENT", 0.90, "filename_rule"
        if "udyam" in fn_lower or "msme" in fn_lower:
            return "UDYAM_DOCUMENT", 0.90, "filename_rule"
        if "mca" in fn_lower or "incorporation" in fn_lower:
            return "MCA_DOCUMENT", 0.90, "filename_rule"
        if "financial" in fn_lower or "turnover" in fn_lower or "balance" in fn_lower:
            return "FINANCIAL_DOCUMENT", 0.85, "filename_rule"
        if "tender" in fn_lower or "nit" in fn_lower:
            return "TENDER_DOCUMENT", 0.85, "filename_rule"

        # 2. Text Keyword / Regex matching
        best_type = "OTHER"
        max_matches = 0
        total_signals = 0

        for doc_type, regex_list in SIGNALS.items():
            matches = 0
            for pattern in regex_list:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches += 1
            if matches > max_matches:
                max_matches = matches
                best_type = doc_type
                total_signals = len(regex_list)

        if max_matches > 0:
            confidence = min(0.95, round(0.50 + (max_matches / total_signals) * 0.45, 2))
            return best_type, confidence, "regex_signal"

        # 3. Fallback to OTHER with low confidence
        return "OTHER", 0.30, "fallback"

document_classifier = DocumentClassifierService()
