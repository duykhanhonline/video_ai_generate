import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.asset import Asset
from app.models.clip import Clip
from app.models.completed_video import CompletedVideo
from app.models.job import Job
from app.models.master_theme import MasterTheme
from app.models.music_track import MusicTrack
from app.models.project import Project
from app.models.prompt_version import PromptVersion
from app.models.user import User
from app.models.video_feedback import VideoFeedback
from app.providers.registry import get_llm_provider
from app.schemas.asset import AssetRead
from app.schemas.clip import ClipRead, ClipUpdate, ImageGenerateRequest
from app.schemas.completed_video import CompletedVideoRead
from app.schemas.job import JobRead
from app.schemas.render_manifest import RenderManifest
from app.schemas.video_feedback import VideoFeedbackRead, VideoFeedbackUpsert
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


@router.get("/{clip_id}/images", response_model=list[AssetRead])
def list_clip_images(clip_id: int, db: Session = Depends(get_db)) -> list[Asset]:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    return list(
        db.scalars(
            select(Asset)
            .where(Asset.clip_id == clip_id, Asset.asset_type == "generated_image")
            .order_by(Asset.created_at.desc())
        ).all()
    )


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
        clip_id=clip_id,
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


def _to_completed_video_read(video: CompletedVideo, asset: Asset) -> CompletedVideoRead:
    return CompletedVideoRead(
        id=video.id,
        clip_id=video.clip_id,
        asset_id=video.asset_id,
        file_path=asset.file_path,
        mime_type=asset.mime_type,
        created_at=video.created_at,
    )


@router.post("/{clip_id}/completed-videos/upload", response_model=CompletedVideoRead, status_code=201)
async def upload_completed_video(
    clip_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
) -> CompletedVideoRead:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video.")

    project = db.get(Project, clip.project_id)

    data = await file.read()
    extension = Path(file.filename or "").suffix or ".mp4"
    filename = f"clip_{clip_id}_completed_{uuid.uuid4().hex[:8]}{extension}"

    storage = StorageService()
    relative_path = storage.save_project_file(project.id, "renders", filename, data)

    asset = Asset(
        project_id=project.id,
        clip_id=clip_id,
        asset_type="completed_video",
        provider="manual",
        provider_model="manual",
        file_path=relative_path,
        mime_type=file.content_type or "video/mp4",
    )
    db.add(asset)
    db.flush()

    completed_video = CompletedVideo(clip_id=clip_id, asset_id=asset.id)
    db.add(completed_video)
    db.commit()
    db.refresh(completed_video)
    db.refresh(asset)

    return _to_completed_video_read(completed_video, asset)


@router.get("/{clip_id}/completed-videos", response_model=list[CompletedVideoRead])
def list_completed_videos(clip_id: int, db: Session = Depends(get_db)) -> list[CompletedVideoRead]:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    rows = db.execute(
        select(CompletedVideo, Asset)
        .join(Asset, CompletedVideo.asset_id == Asset.id)
        .where(CompletedVideo.clip_id == clip_id)
        .order_by(CompletedVideo.created_at.desc())
    ).all()
    return [_to_completed_video_read(video, asset) for video, asset in rows]


@router.delete("/completed-videos/{completed_video_id}", status_code=204)
def delete_completed_video(completed_video_id: int, db: Session = Depends(get_db)) -> None:
    completed_video = db.get(CompletedVideo, completed_video_id)
    if completed_video is None:
        raise HTTPException(status_code=404, detail="Completed video not found")

    asset = db.get(Asset, completed_video.asset_id)

    db.delete(completed_video)
    db.flush()

    if asset is not None:
        StorageService().delete_file(asset.file_path)
        db.delete(asset)

    db.commit()


def _to_video_feedback_read(feedback: VideoFeedback, reviewer: User) -> VideoFeedbackRead:
    return VideoFeedbackRead(
        id=feedback.id,
        completed_video_id=feedback.completed_video_id,
        reviewer_id=feedback.reviewer_id,
        reviewer_name=reviewer.name or reviewer.email,
        feedback_text=feedback.feedback_text,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )


@router.get("/completed-videos/{completed_video_id}/feedback", response_model=list[VideoFeedbackRead])
def list_video_feedback(
    completed_video_id: int, db: Session = Depends(get_db)
) -> list[VideoFeedbackRead]:
    video = db.get(CompletedVideo, completed_video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Completed video not found")

    rows = db.execute(
        select(VideoFeedback, User)
        .join(User, VideoFeedback.reviewer_id == User.id)
        .where(VideoFeedback.completed_video_id == completed_video_id)
        .order_by(VideoFeedback.created_at.desc())
    ).all()
    return [_to_video_feedback_read(feedback, reviewer) for feedback, reviewer in rows]


@router.put("/completed-videos/{completed_video_id}/feedback", response_model=VideoFeedbackRead)
def upsert_video_feedback(
    completed_video_id: int,
    payload: VideoFeedbackUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoFeedbackRead:
    if current_user.role != "reviewer":
        raise HTTPException(status_code=403, detail="Reviewer role required")

    video = db.get(CompletedVideo, completed_video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Completed video not found")

    feedback = db.scalars(
        select(VideoFeedback).where(
            VideoFeedback.completed_video_id == completed_video_id,
            VideoFeedback.reviewer_id == current_user.id,
        )
    ).first()

    if feedback is None:
        feedback = VideoFeedback(
            completed_video_id=completed_video_id,
            reviewer_id=current_user.id,
            feedback_text=payload.feedback_text,
        )
        db.add(feedback)
    else:
        feedback.feedback_text = payload.feedback_text

    db.commit()
    db.refresh(feedback)

    return _to_video_feedback_read(feedback, current_user)


@router.patch("/{clip_id}", response_model=ClipRead)
def update_clip(clip_id: int, payload: ClipUpdate, db: Session = Depends(get_db)) -> Clip:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "approved" in update_data:
        if update_data["approved"] and clip.image_asset_id is None and clip.video_asset_id is None:
            raise HTTPException(
                status_code=400,
                detail="Clip has no generated image or video yet. Nothing to approve.",
            )
        clip.approved = update_data["approved"]

    if "image_prompt" in update_data:
        new_prompt = update_data["image_prompt"]
        if new_prompt != clip.image_prompt:
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
                    provider="manual",
                    model="manual",
                    prompt=new_prompt,
                    version=next_version,
                )
            )
            clip.image_prompt = new_prompt

    if "image_ratio" in update_data:
        clip.image_ratio = update_data["image_ratio"]

    if "reference_image_path" in update_data:
        new_reference_path = update_data["reference_image_path"]
        if new_reference_path:
            full_path = Path(get_settings().media_root) / new_reference_path
            if not full_path.is_file():
                raise HTTPException(
                    status_code=400, detail=f"Reference image not found: {new_reference_path}"
                )
        clip.reference_image_path = new_reference_path

    if "image_asset_id" in update_data and update_data["image_asset_id"] is not None:
        asset_id = update_data["image_asset_id"]
        asset = db.get(Asset, asset_id)
        if (
            asset is None
            or asset.clip_id != clip_id
            or asset.asset_type != "generated_image"
        ):
            raise HTTPException(
                status_code=400, detail="Asset does not belong to this clip's image history."
            )
        clip.image_asset_id = asset.id

    db.commit()
    db.refresh(clip)
    return clip


@router.delete("/{clip_id}", status_code=204)
def delete_clip(clip_id: int, db: Session = Depends(get_db)) -> None:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    storage = StorageService()

    # Break the clip -> asset pointers first so the assets below can be
    # deleted without violating the assets.clip_id -> clips.id foreign key.
    clip.image_asset_id = None
    clip.video_asset_id = None
    db.flush()

    # Clip/Asset/PromptVersion/Job have no ORM relationship() declared between
    # them (plain FK columns only), so SQLAlchemy's unit-of-work can't infer
    # delete order automatically. Flush after each group so the dependent
    # rows are actually gone in the database before the next delete runs.
    assets = db.scalars(select(Asset).where(Asset.clip_id == clip_id)).all()
    for asset in assets:
        storage.delete_file(asset.file_path)
        db.delete(asset)
    db.flush()

    prompt_versions = db.scalars(
        select(PromptVersion).where(PromptVersion.clip_id == clip_id)
    ).all()
    for prompt_version in prompt_versions:
        db.delete(prompt_version)
    db.flush()

    jobs = db.scalars(select(Job).where(Job.clip_id == clip_id)).all()
    for job in jobs:
        db.delete(job)
    db.flush()

    db.delete(clip)
    db.commit()


@router.get("/{clip_id}/render-manifest", response_model=RenderManifest)
def export_clip_render_manifest(clip_id: int, db: Session = Depends(get_db)) -> RenderManifest:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")
    if not clip.approved or clip.video_asset_id is None:
        raise HTTPException(
            status_code=400, detail="Clip has no approved video yet. Nothing to export."
        )

    project = db.get(Project, clip.project_id)
    video_asset = db.get(Asset, clip.video_asset_id)

    music_paths = db.scalars(
        select(Asset.file_path)
        .join(MusicTrack, MusicTrack.asset_id == Asset.id)
        .where(MusicTrack.project_id == project.id, MusicTrack.approved.is_(True))
        .order_by(MusicTrack.id)
    ).all()

    manifest = RenderManifest(
        project_id=project.id,
        clip_id=clip.id,
        project_name=project.name,
        target_duration=project.target_duration,
        videos=[video_asset.file_path],
        music=list(music_paths),
    )

    StorageService().save_file(
        f"manifest/{project.id}_{clip.id}_manifest.json",
        json.dumps(manifest.model_dump(), indent=2).encode(),
    )

    # Make the export visible as a job right away, so the UI can distinguish
    # "exported, waiting for the host agent to pick it up" from "no agent is
    # running at all" -- both currently look like silence otherwise. Don't
    # duplicate if one's already pending/running for this clip (e.g. the
    # user clicked Export again before the agent got to the first one).
    existing_active_job = db.scalars(
        select(Job).where(
            Job.clip_id == clip_id,
            Job.job_type == "render_video",
            Job.status.in_(["PENDING", "RUNNING"]),
        )
    ).first()
    if existing_active_job is None:
        db.add(
            Job(
                project_id=project.id,
                clip_id=clip.id,
                job_type="render_video",
                provider="host_ffmpeg",
                status="PENDING",
            )
        )
        db.commit()

    return manifest


@router.post("/{clip_id}/render-jobs", response_model=JobRead, status_code=200)
def create_clip_render_job(clip_id: int, db: Session = Depends(get_db)) -> Job:
    clip = db.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status_code=404, detail="Clip not found")

    # A PENDING job was created when the manifest was exported (see
    # export_clip_render_manifest above) -- transition that to RUNNING
    # instead of creating a second job, so the export-time job doesn't sit
    # there stale once rendering actually starts.
    pending_job = db.scalars(
        select(Job)
        .where(
            Job.clip_id == clip_id,
            Job.job_type == "render_video",
            Job.status == "PENDING",
        )
        .order_by(Job.created_at.desc())
    ).first()

    if pending_job is not None:
        pending_job.status = "RUNNING"
        pending_job.started_at = datetime.now(UTC)
        db.commit()
        db.refresh(pending_job)
        return pending_job

    job = Job(
        project_id=clip.project_id,
        clip_id=clip.id,
        job_type="render_video",
        provider="host_ffmpeg",
        status="RUNNING",
        started_at=datetime.now(UTC),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
