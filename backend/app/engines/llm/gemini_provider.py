"""
Google Gemini LLM Provider.
"""
import json
import structlog
from typing import Optional, Dict, Any, Type, Tuple
from pydantic import BaseModel

from app.core.config import settings
from app.engines.llm.base import LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)

class GeminiProvider(LLMProvider):
    provider_name: str = "GEMINI"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Tuple[BaseModel, LLMResponse]:
        if not self.api_key:
            raise ValueError("Gemini API Key is missing.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)

        model_inst = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_instruction or "You are an expert procurement intelligence extraction system.",
        )

        schema_json = json.dumps(response_schema.model_json_schema())
        full_prompt = f"Return ONLY valid JSON matching this schema:\n{schema_json}\n\nTask/Prompt:\n{prompt}"

        response = await model_inst.generate_content_async(
            full_prompt,
            generation_config={"response_mime_type": "application/json", "temperature": temperature},
        )

        content = response.text or "{}"
        parsed = json.loads(content)
        instance = response_schema.model_validate(parsed)

        llm_resp = LLMResponse(
            content=content,
            parsed_json=parsed,
            model_name=self.model,
            provider_name=self.provider_name,
            is_mock=False,
        )
        return instance, llm_resp
