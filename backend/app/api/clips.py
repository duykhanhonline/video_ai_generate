import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.clip import Clip
from app.models.job import Job
from app.models.master_theme import MasterTheme
from app.models.project import Project
from app.models.prompt_version import PromptVersion
from app.providers.registry import get_llm_provider
from app.schemas.clip import ClipRead, ImageGenerateRequest
from app.schemas.job import JobRead
from app.services.director_service import AIDirectorService
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
