"""
Rule-Based Deterministic Field Extractor.

Extracts high-precision identifiers & numeric patterns:
- PAN (e.g. AADCB2230M)
- GSTIN (e.g. 27AADCB2230M1ZP)
- CIN (e.g. U72900MH2020PTC345678)
- Udyam Number (e.g. UDYAM-MH-01-0000001)
- Email & Phone numbers
- Financial turnover figures (INR / Cr)
"""
import re
import structlog
from typing import List, Dict, Any, Optional

from app.engines.extraction.schemas import ExtractedFieldContract, ExtractionMethod

logger = structlog.get_logger(__name__)

# Strict regex patterns
REGEX_PAN = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
REGEX_GSTIN = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b"
REGEX_CIN = r"\b[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b"
REGEX_UDYAM = r"\bUDYAM-[A-Z]{2}-\d{2}-\d{7}\b"
REGEX_EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
REGEX_PHONE = r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b"
REGEX_TURNOVER = r"(?:annual\s+turnover|turnover)[:\s]*₹?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr|lakh|lakhs|lakh|inr)?"

class RuleExtractorService:
    def extract_from_page(self, page_text: str, page_number: int) -> List[ExtractedFieldContract]:
        fields: List[ExtractedFieldContract] = []
        if not page_text:
            return fields

        # 1. PAN
        for match in re.finditer(REGEX_PAN, page_text):
            val = match.group(0).upper()
            start = max(0, match.start() - 30)
            end = min(len(page_text), match.end() + 30)
            excerpt = page_text[start:end].strip()
            fields.append(ExtractedFieldContract(
                field_name="pan",
                field_value=val,
                field_value_normalized=val,
                data_type="string",
                confidence=0.99,
                page_number=page_number,
                text_excerpt=excerpt,
                extraction_method=ExtractionMethod.REGEX,
                validation_status="VALID",
            ))

        # 2. GSTIN
        for match in re.finditer(REGEX_GSTIN, page_text):
            val = match.group(0).upper()
            start = max(0, match.start() - 30)
            end = min(len(page_text), match.end() + 30)
            excerpt = page_text[start:end].strip()
            fields.append(ExtractedFieldContract(
                field_name="gstin",
                field_value=val,
                field_value_normalized=val,
                data_type="string",
                confidence=0.99,
                page_number=page_number,
                text_excerpt=excerpt,
                extraction_method=ExtractionMethod.REGEX,
                validation_status="VALID",
            ))

        # 3. CIN
        for match in re.finditer(REGEX_CIN, page_text):
            val = match.group(0).upper()
            start = max(0, match.start() - 30)
            end = min(len(page_text), match.end() + 30)
            excerpt = page_text[start:end].strip()
            fields.append(ExtractedFieldContract(
                field_name="cin",
                field_value=val,
                field_value_normalized=val,
                data_type="string",
                confidence=0.99,
                page_number=page_number,
                text_excerpt=excerpt,
                extraction_method=ExtractionMethod.REGEX,
                validation_status="VALID",
            ))

        # 4. Udyam
        for match in re.finditer(REGEX_UDYAM, page_text, re.IGNORECASE):
            val = match.group(0).upper()
            start = max(0, match.start() - 30)
            end = min(len(page_text), match.end() + 30)
            excerpt = page_text[start:end].strip()
            fields.append(ExtractedFieldContract(
                field_name="udyam_number",
                field_value=val,
                field_value_normalized=val,
                data_type="string",
                confidence=0.99,
                page_number=page_number,
                text_excerpt=excerpt,
                extraction_method=ExtractionMethod.REGEX,
                validation_status="VALID",
            ))

        # 5. Email
        for match in re.finditer(REGEX_EMAIL, page_text):
            val = match.group(0).lower()
            start = max(0, match.start() - 20)
            end = min(len(page_text), match.end() + 20)
            excerpt = page_text[start:end].strip()
            fields.append(ExtractedFieldContract(
                field_name="email",
                field_value=val,
                field_value_normalized=val,
                data_type="string",
                confidence=0.95,
                page_number=page_number,
                text_excerpt=excerpt,
                extraction_method=ExtractionMethod.REGEX,
                validation_status="VALID",
            ))

        # 6. Financial Turnover
        for match in re.finditer(REGEX_TURNOVER, page_text, re.IGNORECASE):
            raw_val = match.group(1).replace(",", "")
            unit = (match.group(2) or "").lower()
            try:
                num_val = float(raw_val)
                # Convert crore to base INR if unit is crore
                if "cr" in unit or "crore" in unit:
                    num_val_inr = num_val * 10_000_000
                elif "lakh" in unit:
                    num_val_inr = num_val * 100_000
                else:
                    num_val_inr = num_val

                start = max(0, match.start() - 30)
                end = min(len(page_text), match.end() + 30)
                excerpt = page_text[start:end].strip()

                fields.append(ExtractedFieldContract(
                    field_name="annual_turnover_inr",
                    field_value=str(num_val_inr),
                    field_value_normalized=str(num_val_inr),
                    data_type="number",
                    confidence=0.90,
                    page_number=page_number,
                    text_excerpt=excerpt,
                    extraction_method=ExtractionMethod.REGEX,
                    validation_status="VALID",
                ))
            except Exception:
                pass

        return fields

rule_extractor = RuleExtractorService()
