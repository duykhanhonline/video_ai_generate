import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.models.clip import Clip
from app.models.job import Job
from app.models.music_track import MusicTrack
from app.models.project import Project
from app.schemas.job import JobRead
from app.schemas.render_manifest import RenderManifest
from app.services.storage_service import StorageService

router = APIRouter(prefix="/api/projects", tags=["render"])


def _build_render_manifest(project: Project, db: Session) -> RenderManifest:
    video_paths = db.scalars(
        select(Asset.file_path)
        .join(Clip, Clip.video_asset_id == Asset.id)
        .where(Clip.project_id == project.id, Clip.approved.is_(True))
        .order_by(Clip.id)
    ).all()

    music_paths = db.scalars(
        select(Asset.file_path)
        .join(MusicTrack, MusicTrack.asset_id == Asset.id)
        .where(MusicTrack.project_id == project.id)
        .order_by(MusicTrack.id)
    ).all()

    return RenderManifest(
        project_id=project.id,
        project_name=project.name,
        target_duration=project.target_duration,
        videos=list(video_paths),
        music=list(music_paths),
    )


@router.get("/{project_id}/render-manifest", response_model=RenderManifest)
def export_render_manifest(project_id: int, db: Session = Depends(get_db)) -> RenderManifest:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    manifest = _build_render_manifest(project, db)

    storage = StorageService()
    storage.save_project_file(
        project.id,
        "manifests",
        "manifest.json",
        json.dumps(manifest.model_dump(), indent=2).encode(),
    )

    return manifest


@router.get("/{project_id}/render-jobs", response_model=list[JobRead])
def list_render_jobs(project_id: int, db: Session = Depends(get_db)) -> list[Job]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return list(
        db.scalars(
            select(Job)
            .where(Job.project_id == project_id, Job.job_type == "render_video")
            .order_by(Job.created_at.desc())
        ).all()
    )


@router.post("/{project_id}/render-jobs", response_model=JobRead, status_code=201)
def create_render_job(project_id: int, db: Session = Depends(get_db)) -> Job:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    job = Job(
        project_id=project.id,
        job_type="render_video",
        provider="host_ffmpeg",
        status="RUNNING",
        started_at=datetime.now(UTC),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
