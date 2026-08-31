"""
Policy Copilot Service.

Provides evidence-grounded policy intelligence:
- Policy Question Answering with Citations
- Policy Source/Version Comparison
- Contextual Bidder Explanation (Bidder Data + Requirement + Policy Evidence + Deterministic Result)

CRITICAL GOVERNANCE RULE:
Deterministic compliance engine remains authoritative.
Copilot explains the result based on retrieved policy evidence.
"""
import structlog
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.policy.retriever import HybridPolicyRetriever
from app.engines.policy.answerer import policy_answerer
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)

class PolicyCopilotService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def ask_policy(
        self,
        question: str,
        source_filters: Optional[List[str]] = None,
        version_filter: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        retriever = HybridPolicyRetriever(self.db)
        chunks = await retriever.retrieve(question, source_filter=source_filters, version_filter=version_filter)

        res = await policy_answerer.generate_answer(question, chunks)

        await self.audit.log(
            action=AuditAction.POLICY_QUERY,
            action_category=AuditCategory.SYSTEM,
            user_id=user_id,
            new_value={"question": question[:100], "grounding": res["grounding"]},
            change_summary="Officer executed Policy RAG query.",
        )
        return res

    async def compare_sources(
        self,
        source_a: str,
        version_a: str,
        source_b: str,
        version_b: str,
        topic: str,
    ) -> Dict[str, Any]:
        retriever = HybridPolicyRetriever(self.db)
        chunks_a = await retriever.retrieve(topic, source_filter=[source_a], version_filter=version_a)
        chunks_b = await retriever.retrieve(topic, source_filter=[source_b], version_filter=version_b)

        text_a = chunks_a[0].text if chunks_a else "No data for source A"
        text_b = chunks_b[0].text if chunks_b else "No data for source B"

        is_conflict = (text_a != text_b) and (chunks_a and chunks_b)

        return {
            "topic": topic,
            "source_a": {"code": source_a, "version": version_a, "excerpt": text_a[:200]},
            "source_b": {"code": source_b, "version": version_b, "excerpt": text_b[:200]},
            "has_conflict": is_conflict,
            "analysis": f"Comparison between {source_a} ({version_a}) and {source_b} ({version_b}) on topic '{topic}'.",
        }

    async def generate_contextual_bidder_explanation(
        self,
        bid_id: str,
        requirement_name: str,
        extracted_value: str,
        required_value: str,
        compliance_result: str,
    ) -> Dict[str, Any]:
        """
        Combines Bidder Evidence + Tender Requirement + Policy Evidence + Deterministic Result.
        """
        retriever = HybridPolicyRetriever(self.db)
        chunks = await retriever.retrieve(requirement_name, top_k=3)

        policy_res = await policy_answerer.generate_answer(requirement_name, chunks)

        explanation_text = (
            f"Requirement: '{requirement_name}' (Required: {required_value}).\n"
            f"Extracted Bidder Evidence: {extracted_value}.\n"
            f"Deterministic Compliance System Result: {compliance_result}.\n\n"
            f"Policy Context ({policy_res.get('citations', [{}])[0].get('source', 'Policy')}): {policy_res.get('answer')}"
        )

        return {
            "bid_id": bid_id,
            "requirement_name": requirement_name,
            "extracted_value": extracted_value,
            "required_value": required_value,
            "compliance_result": compliance_result,
            "explanation": explanation_text,
            "policy_citations": policy_res.get("citations", []),
            "authority": "Deterministic Compliance Engine (Rule Calculation)",
        }

policy_copilot = PolicyCopilotService
