"""
LLM Abstraction Architecture Base.

Provider-agnostic interface for structured AI extraction & classification.
Enforces:
- Structured JSON output parsing
- Pydantic schema validation
- Token usage & model version tracking
- Deterministic fallback options
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, Type, TypeVar, Tuple
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

@dataclass
class LLMResponse:
    content: str
    parsed_json: Optional[Dict[str, Any]]
    model_name: str
    provider_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    is_mock: bool = False
    error: Optional[str] = None

class LLMProvider(ABC):
    provider_name: str = "ABSTRACT"

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Tuple[T, LLMResponse]:
        """Generates structured JSON validated against a Pydantic schema."""
        ...
