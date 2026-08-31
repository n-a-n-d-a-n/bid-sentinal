"""
Evidence-Grounded Policy Answerer.

Combines:
- Strict Grounding System Prompt
- LLM Provider Abstraction
- Abstention Logic (INSUFFICIENT_EVIDENCE)
- Structured Citation & Grounding Envelope
"""
import structlog
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.engines.llm import get_llm_provider
from app.engines.policy.retriever import RetrievedChunk
from app.engines.policy.context_builder import context_builder
from app.engines.policy.citation import citation_engine
from app.engines.policy.guardrails import policy_guardrails

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are PROCUREX Policy Intelligence Assistant.
Answer ONLY from the supplied policy evidence.
If the evidence does not support the answer, say:
'The available policy sources do not provide sufficient evidence to answer this question.'
Never invent policy provisions, thresholds, section numbers, dates, or citations.
Every substantive claim must be supported by a supplied source.
Do not make final procurement decisions.
"""

class PolicyAnswerSchema(BaseModel):
    answer: str = Field(..., description="Grounded answer to the policy question")
    confidence: str = Field("HIGH", description="HIGH | MEDIUM | LOW | INSUFFICIENT_EVIDENCE")
    limitations: List[str] = Field(default_factory=list)

class PolicyAnswererService:
    async def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[RetrievedChunk],
        provider_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        
        # 1. Input sanitization
        clean_q = policy_guardrails.sanitize_input(question)

        # 2. Check for empty/low relevance retrieval -> ABSTAIN
        if not retrieved_chunks or (retrieved_chunks[0].similarity < 0.20):
            return {
                "answer": "The available policy sources do not provide sufficient evidence to answer this question.",
                "grounding": "INSUFFICIENT_EVIDENCE",
                "confidence": "INSUFFICIENT_EVIDENCE",
                "citations": [],
                "retrieved_chunks": len(retrieved_chunks),
                "limitations": ["No sufficiently relevant policy passages found in knowledge base."],
            }

        # 3. Build Context & Citations
        context_str = context_builder.build_context_text(retrieved_chunks)
        citations = citation_engine.generate_citations(retrieved_chunks)

        # 4. LLM Generation
        provider = get_llm_provider(provider_name)
        full_prompt = f"{context_str}\n\nOfficer Question:\n{clean_q}"

        try:
            instance, llm_resp = await provider.generate_structured(
                prompt=full_prompt,
                response_schema=PolicyAnswerSchema,
                system_instruction=SYSTEM_PROMPT,
            )
            grounding_status = policy_guardrails.verify_grounding(instance.answer, context_str)

            return {
                "answer": instance.answer,
                "grounding": grounding_status,
                "confidence": instance.confidence,
                "citations": citations,
                "retrieved_chunks": len(retrieved_chunks),
                "limitations": instance.limitations,
            }
        except Exception as exc:
            logger.warning("policy_answerer_fallback", error=str(exc))
            # Safe Fallback Answer
            top_c = retrieved_chunks[0]
            fallback_ans = f"Based on {top_c.source_code} ({top_c.version}), Section '{top_c.section}', Page {top_c.page_number}: {top_c.text[:300]}"
            return {
                "answer": fallback_ans,
                "grounding": "GROUNDED",
                "confidence": "MEDIUM",
                "citations": citations,
                "retrieved_chunks": len(retrieved_chunks),
                "limitations": [f"Fallback response generated: {str(exc)}"],
            }

policy_answerer = PolicyAnswererService()
