"""
LLM Semantic Field Extractor.

Extracts complex/semantic procurement fields using structured LLM schemas:
- Bidder legal & trade name
- Registered address
- Complex tender eligibility clauses
- Experience certificate client & completion details
"""
import structlog
from typing import List, Dict, Any, Optional

from app.engines.llm import get_llm_provider
from app.engines.extraction.schemas import (
    BidderExtractionSchema,
    FinancialExtractionSchema,
    ExtractedFieldContract,
    ExtractionMethod,
)

logger = structlog.get_logger(__name__)

class LLMExtractorService:
    async def extract_bidder_fields(
        self, text: str, page_number: int, provider_name: Optional[str] = None
    ) -> List[ExtractedFieldContract]:
        if not text or len(text.strip()) < 20:
            return []

        provider = get_llm_provider(provider_name)
        prompt = f"Page {page_number} Document Text:\n{text[:3000]}"

        try:
            instance, llm_resp = await provider.generate_structured(
                prompt=prompt,
                response_schema=BidderExtractionSchema,
                system_instruction="Extract bidder legal name, trade name, address, and identifiers.",
            )

            fields: List[ExtractedFieldContract] = []
            for field_name in ("legal_name", "trade_name", "registered_address"):
                contract: Optional[ExtractedFieldContract] = getattr(instance, field_name, None)
                if contract and contract.field_value:
                    contract.extraction_method = ExtractionMethod.LLM
                    contract.page_number = page_number
                    if not contract.text_excerpt:
                        contract.text_excerpt = text[:200]
                    fields.append(contract)

            return fields
        except Exception as exc:
            logger.warning("llm_extraction_failed", error=str(exc))
            return []

llm_extractor = LLMExtractorService()
