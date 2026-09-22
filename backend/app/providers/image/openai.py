from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.providers.base.image import ImageProvider


class OpenAIImageProvider(ImageProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._media_root = Path(settings.media_root)
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
        size: str = "1024x1024",
        reference_images: list[str] | None = None,
    ) -> str:
        if reference_images:
            reference_path = self._media_root / reference_images[0]
            if not reference_path.is_file():
                raise FileNotFoundError(f"Reference image not found: {reference_images[0]}")
            with reference_path.open("rb") as reference_file:
                response = await self._client.images.edit(
                    model=self._model,
                    image=reference_file,
                    prompt=prompt,
                    size=size,
                    n=1,
                )
        else:
            response = await self._client.images.generate(
                model=self._model,
                prompt=prompt,
                size=size,
                n=1,
            )
        return response.data[0].b64_json
