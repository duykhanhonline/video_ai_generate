from pathlib import Path

from app.core.config import get_settings


class StorageService:
    def __init__(self, media_root: str | Path | None = None) -> None:
        self._media_root = Path(media_root) if media_root is not None else Path(get_settings().media_root)

    def save_project_file(self, project_id: int, subdir: str, filename: str, data: bytes) -> str:
        relative_path = f"projects/{project_id}/{subdir}/{filename}"
        full_path = self._media_root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        return relative_path

    def delete_file(self, relative_path: str) -> None:
        full_path = self._media_root / relative_path
        full_path.unlink(missing_ok=True)
