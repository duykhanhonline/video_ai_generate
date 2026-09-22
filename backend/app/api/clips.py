import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.asset import Asset
from app.models.clip import Clip
from app.models.job import Job
from app.models.master_theme import MasterTheme
from app.models.project import Project
from app.models.prompt_version import PromptVersion
from app.providers.registry import get_llm_provider
from app.schemas.clip import ClipRead, ClipUpdate, ImageGenerateRequest
from app.schemas.job import JobRead
from app.services.director_service import AIDirectorService
from app.services.storage_service import StorageService
from app.workers.image_tasks import generate_clip_image_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clips", tags=["clips"])


@router.post("/{clip_id}/image-prompt/generate", response_model=ClipRead)
async def generate_image_prompt(clip_id: int, db: Session = Depends(get_db)) -> Clip:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    project = db.get(Project, clip.project_id)
    theme = db.get(MasterTheme, project.master_theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    try:
        llm_provider = get_llm_provider()
        director = AIDirectorService(llm_provider=llm_provider)
        draft = await director.generate_image_prompt(theme, clip.activity)
    except Exception:
        logger.exception("AI Director image prompt generation failed")
        raise HTTPException(
            status_code=502, detail="AI Director generation failed. Check LLM provider configuration."
        ) from None

    existing_versions = db.scalars(
        select(PromptVersion.version).where(
            PromptVersion.clip_id == clip_id, PromptVersion.prompt_type == "image"
        )
    ).all()
    next_version = max(existing_versions, default=0) + 1

    db.add(
        PromptVersion(
            project_id=clip.project_id,
            clip_id=clip_id,
            prompt_type="image",
            provider=llm_provider.provider_name,
            model=llm_provider.model_name,
            prompt=draft.prompt,
            version=next_version,
        )
    )
    clip.image_prompt = draft.prompt
    db.commit()
    db.refresh(clip)
    return clip


@router.post("/{clip_id}/video-prompt/generate", response_model=ClipRead)
async def generate_video_prompt(clip_id: int, db: Session = Depends(get_db)) -> Clip:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not clip.approved:
        raise HTTPException(
            status_code=400,
            detail="Clip's image must be approved before generating a video prompt.",
        )
    if not clip.image_prompt:
        raise HTTPException(status_code=400, detail="Clip has no image prompt yet.")

    project = db.get(Project, clip.project_id)
    theme = db.get(MasterTheme, project.master_theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    try:
        llm_provider = get_llm_provider()
        director = AIDirectorService(llm_provider=llm_provider)
        draft = await director.generate_video_prompt(theme, clip.activity, clip.image_prompt)
    except Exception:
        logger.exception("AI Director video prompt generation failed")
        raise HTTPException(
            status_code=502, detail="AI Director generation failed. Check LLM provider configuration."
        ) from None

    existing_versions = db.scalars(
        select(PromptVersion.version).where(
            PromptVersion.clip_id == clip_id, PromptVersion.prompt_type == "video"
        )
    ).all()
    next_version = max(existing_versions, default=0) + 1

    db.add(
        PromptVersion(
            project_id=clip.project_id,
            clip_id=clip_id,
            prompt_type="video",
            provider=llm_provider.provider_name,
            model=llm_provider.model_name,
            prompt=draft.prompt,
            version=next_version,
        )
    )
    clip.video_prompt = draft.prompt
    db.commit()
    db.refresh(clip)
    return clip


@router.post("/{clip_id}/image/generate", response_model=JobRead, status_code=202)
def generate_clip_image(
    clip_id: int, payload: ImageGenerateRequest, db: Session = Depends(get_db)
) -> Job:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not clip.image_prompt:
        raise HTTPException(
            status_code=400, detail="Clip has no image prompt yet. Generate one first."
        )
    if clip.image_asset_id is not None and not payload.force:
        raise HTTPException(
            status_code=409,
            detail="Clip already has a generated image. Pass force=true to regenerate.",
        )

    project = db.get(Project, clip.project_id)

    job = Job(
        project_id=project.id,
        clip_id=clip_id,
        job_type="generate_image",
        provider=project.image_provider,
        status="PENDING",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    generate_clip_image_task.delay(job.id, clip_id)

    return job


@router.post("/{clip_id}/video/upload", response_model=ClipRead)
async def upload_clip_video(
    clip_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> Clip:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video.")

    project = db.get(Project, clip.project_id)

    data = await file.read()
    extension = Path(file.filename or "").suffix or ".mp4"
    filename = f"clip_{clip_id}_{uuid.uuid4().hex[:8]}{extension}"

    storage = StorageService()
    relative_path = storage.save_project_file(project.id, "videos", filename, data)

    asset = Asset(
        project_id=project.id,
        asset_type="generated_video",
        provider="manual",
        provider_model="manual",
        file_path=relative_path,
        mime_type=file.content_type or "video/mp4",
    )
    db.add(asset)
    db.flush()

    clip.video_asset_id = asset.id
    clip.status = "video_generated"
    db.commit()
    db.refresh(clip)
    return clip


@router.patch("/{clip_id}", response_model=ClipRead)
def update_clip(clip_id: int, payload: ClipUpdate, db: Session = Depends(get_db)) -> Clip:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if payload.approved and clip.image_asset_id is None:
        raise HTTPException(
            status_code=400, detail="Clip has no generated image yet. Nothing to approve."
        )

    clip.approved = payload.approved
    db.commit()
    db.refresh(clip)
    return clip
