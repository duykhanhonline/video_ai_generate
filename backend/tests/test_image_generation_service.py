import base64
from pathlib import Path

from app.providers.base.image import ImageProvider
from app.services.image_generation_service import ImageGenerationService
from app.services.storage_service import StorageService


class FakeImageProvider(ImageProvider):
    def __init__(self, image_bytes: bytes) -> None:
        self._image_b64 = base64.b64encode(image_bytes).decode()

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-model"

    async def generate(
        self, prompt: str, size: str = "1024x1024", reference_images: list[str] | None = None
    ) -> str:
        return self._image_b64


async def test_generate_clip_image_saves_file_and_returns_metadata(tmp_path: Path) -> None:
    provider = FakeImageProvider(b"fake-png-bytes")
    service = ImageGenerationService(provider, StorageService(media_root=tmp_path))

    result = await service.generate_clip_image(project_id=5, clip_id=42, prompt="a calm samurai")

    assert result.provider == "fake"
    assert result.provider_model == "fake-model"
    assert result.mime_type == "image/png"
    assert result.file_path.startswith("projects/5/images/clip_42_")
    saved_file = tmp_path / result.file_path
    assert saved_file.read_bytes() == b"fake-png-bytes"
