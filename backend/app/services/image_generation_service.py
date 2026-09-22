import base64
import uuid
from dataclasses import dataclass

from app.providers.base.image import ImageProvider
from app.services.storage_service import StorageService


@dataclass
class GeneratedImage:
    file_path: str
    mime_type: str
    provider: str
    provider_model: str


class ImageGenerationService:
    def __init__(self, image_provider: ImageProvider, storage_service: StorageService) -> None:
        self._image_provider = image_provider
        self._storage_service = storage_service

    async def generate_clip_image(self, project_id: int, clip_id: int, prompt: str) -> GeneratedImage:
        image_b64 = await self._image_provider.generate(prompt=prompt)
        image_bytes = base64.b64decode(image_b64)
        filename = f"clip_{clip_id}_{uuid.uuid4().hex[:8]}.png"
        relative_path = self._storage_service.save_project_file(project_id, "images", filename, image_bytes)
        return GeneratedImage(
            file_path=relative_path,
            mime_type="image/png",
            provider=self._image_provider.provider_name,
            provider_model=self._image_provider.model_name,
        )
