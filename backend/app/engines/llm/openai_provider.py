"""
OpenAI LLM Provider.
"""
import json
import structlog
from typing import Optional, Dict, Any, Type, Tuple
from pydantic import BaseModel

from app.core.config import settings
from app.engines.llm.base import LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)

class OpenAIProvider(LLMProvider):
    provider_name: str = "OPENAI"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Tuple[BaseModel, LLMResponse]:
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing.")

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key, base_url=settings.OPENAI_BASE_URL)

        schema_json = json.dumps(response_schema.model_json_schema())
        sys_msg = (system_instruction or "You are an expert procurement intelligence extraction system.")
        sys_msg += f"\n\nReturn JSON strictly conforming to this JSON Schema:\n{schema_json}"

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        instance = response_schema.model_validate(parsed)

        llm_resp = LLMResponse(
            content=content,
            parsed_json=parsed,
            model_name=self.model,
            provider_name=self.provider_name,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            is_mock=False,
        )
        return instance, llm_resp
