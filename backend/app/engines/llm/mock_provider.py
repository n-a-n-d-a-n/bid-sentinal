"""
Mock LLM Provider for Demo Mode & Offline Execution.
"""
import json
import structlog
from typing import Optional, Dict, Any, Type, Tuple
from pydantic import BaseModel

from app.engines.llm.base import LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)

class MockLLMProvider(LLMProvider):
    provider_name: str = "MOCK"

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Tuple[BaseModel, LLMResponse]:
        """
        Creates a valid instance of response_schema with mock default values.
        """
        # Try constructing minimal valid instance using model defaults
        sample_dict = {}
        for name, field in response_schema.model_fields.items():
            if field.default is not None and field.default != ...:
                sample_dict[name] = field.default
            elif field.annotation == str or getattr(field.annotation, "__name__", "") == "str":
                sample_dict[name] = f"Mock {name}"
            elif field.annotation == float or field.annotation == int:
                sample_dict[name] = 100.0
            elif field.annotation == bool:
                sample_dict[name] = True
            else:
                sample_dict[name] = None

        try:
            instance = response_schema.model_validate(sample_dict)
        except Exception:
            # Fallback construct with empty construct
            instance = response_schema.model_construct(**sample_dict)

        resp = LLMResponse(
            content=json.dumps(sample_dict),
            parsed_json=sample_dict,
            model_name="mock-engine-v1",
            provider_name=self.provider_name,
            is_mock=True,
        )
        return instance, resp
