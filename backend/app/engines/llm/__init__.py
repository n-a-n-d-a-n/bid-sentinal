"""
LLM Engine Package.
Factory getter function for provider instantiation.
"""
from typing import Optional
from app.core.config import settings
from app.engines.llm.base import LLMProvider, LLMResponse
from app.engines.llm.mock_provider import MockLLMProvider
from app.engines.llm.openai_provider import OpenAIProvider
from app.engines.llm.gemini_provider import GeminiProvider

def get_llm_provider(provider_override: Optional[str] = None) -> LLMProvider:
    provider_name = (provider_override or settings.AI_PROVIDER).lower()

    if provider_name == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider()
    elif provider_name == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider()
    else:
        return MockLLMProvider()

__all__ = [
    "LLMProvider",
    "LLMResponse",
    "MockLLMProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "get_llm_provider",
]
