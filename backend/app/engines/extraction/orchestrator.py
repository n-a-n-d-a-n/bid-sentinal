"""
Extraction Orchestrator.

Combines:
1. Rule / Regex deterministic extraction (High precision, preferred for identifiers)
2. LLM extraction for semantic / complex fields
3. Provenance attachment (source document, page_number, confidence, method)
4. Field reconciliation & deduplication
"""
import structlog
from typing import List, Dict, Any, Optional

from app.engines.extraction.schemas import ExtractedFieldContract, ExtractionMethod, DocumentExtractionResult
from app.engines.extraction.rule_extractor import rule_extractor
from app.engines.extraction.llm_extractor import llm_extractor

logger = structlog.get_logger(__name__)

class ExtractionOrchestratorService:
    async def extract_document_fields(
        self,
        document_id: str,
        document_type: str,
        pages_text: List[Dict[str, Any]],  # list of {"page_number": int, "text": str}
        use_llm: bool = True,
    ) -> DocumentExtractionResult:
        all_extracted: List[ExtractedFieldContract] = []

        # 1. Run deterministic Rule Extraction on every page
        for page_info in pages_text:
            page_num = page_info["page_number"]
            page_text = page_info.get("text", "")
            rule_fields = rule_extractor.extract_from_page(page_text, page_num)
            all_extracted.extend(rule_fields)

        # 2. Run LLM Extraction if enabled and required
        if use_llm:
            for page_info in pages_text[:5]:  # Process top pages for semantic fields
                page_num = page_info["page_number"]
                page_text = page_info.get("text", "")
                llm_fields = await llm_extractor.extract_bidder_fields(page_text, page_num)
                all_extracted.extend(llm_fields)

        # 3. Reconcile & Deduplicate Fields
        # Rules override LLMs for deterministic identifiers (PAN, GSTIN, CIN, Udyam)
        reconciled: Dict[str, ExtractedFieldContract] = {}

        for item in all_extracted:
            fname = item.field_name
            if fname not in reconciled:
                reconciled[fname] = item
            else:
                existing = reconciled[fname]
                # If existing is REGEX/RULE and new is LLM, keep REGEX/RULE
                if existing.extraction_method in (ExtractionMethod.RULE, ExtractionMethod.REGEX):
                    continue
                # If new is REGEX/RULE, replace existing
                elif item.extraction_method in (ExtractionMethod.RULE, ExtractionMethod.REGEX):
                    reconciled[fname] = item
                # Otherwise keep higher confidence
                elif item.confidence > existing.confidence:
                    reconciled[fname] = item

        final_fields = list(reconciled.values())

        return DocumentExtractionResult(
            document_id=document_id,
            document_type=document_type,
            fields=final_fields,
            prompt_version="bidder_v1",
            model_name="extraction_orchestrator_v1",
        )

extraction_orchestrator = ExtractionOrchestratorService()
