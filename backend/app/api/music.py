import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.models.music_track import MusicTrack
from app.models.project import Project
from app.schemas.music_track import MusicTrackRead, MusicTrackUpdate
from app.services.storage_service import StorageService

router = APIRouter(tags=["music"])


def _to_music_track_read(track: MusicTrack, asset: Asset) -> MusicTrackRead:
    return MusicTrackRead(
        id=track.id,
        project_id=track.project_id,
        title=track.title,
        asset_id=track.asset_id,
        file_path=asset.file_path,
        mime_type=asset.mime_type,
        approved=track.approved,
        created_at=track.created_at,
        updated_at=track.updated_at,
    )


@router.get("/api/projects/{project_id}/music", response_model=list[MusicTrackRead])
def list_project_music(project_id: int, db: Session = Depends(get_db)) -> list[MusicTrackRead]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = db.execute(
        select(MusicTrack, Asset)
        .join(Asset, MusicTrack.asset_id == Asset.id)
        .where(MusicTrack.project_id == project_id)
        .order_by(MusicTrack.created_at.desc())
    ).all()
    return [_to_music_track_read(track, asset) for track, asset in rows]


@router.post("/api/projects/{project_id}/music/upload", response_model=MusicTrackRead, status_code=201)
async def upload_music_track(
    project_id: int,
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
) -> MusicTrackRead:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an audio file.")

    data = await file.read()
    extension = Path(file.filename or "").suffix or ".mp3"
    filename = f"track_{uuid.uuid4().hex[:8]}{extension}"

    storage = StorageService()
    relative_path = storage.save_project_file(project.id, "music", filename, data)

    asset = Asset(
        project_id=project.id,
        asset_type="music",
        provider="manual",
        provider_model="manual",
        file_path=relative_path,
        mime_type=file.content_type or "audio/mpeg",
    )
    db.add(asset)
    db.flush()

    track = MusicTrack(project_id=project.id, title=title, asset_id=asset.id)
    db.add(track)
    db.commit()
    db.refresh(track)
    db.refresh(asset)

    return _to_music_track_read(track, asset)


@router.patch("/api/music/{track_id}", response_model=MusicTrackRead)
def update_music_track(
    track_id: int, payload: MusicTrackUpdate, db: Session = Depends(get_db)
) -> MusicTrackRead:
    track = db.get(MusicTrack, track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Music track not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "approved" in update_data:
        track.approved = update_data["approved"]

    db.commit()
    db.refresh(track)

    asset = db.get(Asset, track.asset_id)
    return _to_music_track_read(track, asset)


@router.delete("/api/music/{track_id}", status_code=204)
def delete_music_track(track_id: int, db: Session = Depends(get_db)) -> None:
    track = db.get(MusicTrack, track_id)
    if track is None:
        raise HTTPException(status_code=404, detail="Music track not found")

    asset = db.get(Asset, track.asset_id)

    db.delete(track)
    db.flush()

    if asset is not None:
        StorageService().delete_file(asset.file_path)
        db.delete(asset)

    db.commit()
