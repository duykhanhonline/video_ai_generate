from openai import AsyncOpenAI

from app.core.config import get_settings
from app.providers.base.image import ImageProvider


class OpenAIImageProvider(ImageProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = "gpt-image-1"

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        prompt: str,
        reference_images: list[str] | None = None,
    ) -> str:
        response = await self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        return response.data[0].b64_json
