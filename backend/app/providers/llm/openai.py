import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.providers.base.llm import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = "gpt-4o-mini"

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_response",
                    "schema": json_schema,
                    "strict": True,
                },
            },
        )
        content = response.choices[0].message.content
        return json.loads(content)
