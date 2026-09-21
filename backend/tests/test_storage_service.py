from pathlib import Path

from app.services.storage_service import StorageService


def test_save_project_file_writes_file_and_returns_relative_path(tmp_path: Path) -> None:
    service = StorageService(media_root=tmp_path)

    relative_path = service.save_project_file(12, "images", "clip_1.png", b"fake-image-bytes")

    assert relative_path == "projects/12/images/clip_1.png"
    saved_file = tmp_path / relative_path
    assert saved_file.exists()
    assert saved_file.read_bytes() == b"fake-image-bytes"


def test_save_project_file_creates_missing_directories(tmp_path: Path) -> None:
    service = StorageService(media_root=tmp_path)

    relative_path = service.save_project_file(7, "music", "track_1.mp3", b"fake-audio")

    assert (tmp_path / "projects" / "7" / "music").is_dir()
    assert relative_path == "projects/7/music/track_1.mp3"
