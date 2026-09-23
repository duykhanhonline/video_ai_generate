import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.asset import Asset
from app.models.category import Category
from app.models.clip import Clip
from app.models.completed_video import CompletedVideo
from app.models.master_theme import MasterTheme
from app.models.project import Project
from app.models.user import User
from app.providers.registry import get_llm_provider
from app.schemas.ai_director import ActivityGenerateRequest, ActivityIdeasDraft
from app.schemas.clip import ClipRead, ClipsCreateRequest
from app.schemas.completed_video import ProjectCompletedVideoRead
from app.schemas.project import ProjectCreate, ProjectRead, ProjectReviewSummary
from app.services.director_service import AIDirectorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    theme = db.get(MasterTheme, payload.master_theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    if payload.category_id is not None and db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")

    project = Project(**payload.model_dump(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Project]:
    return list(
        db.scalars(select(Project).where(Project.owner_id == current_user.id)).all()
    )


@router.get("/review-summary", response_model=list[ProjectReviewSummary])
def get_project_review_summary(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ProjectReviewSummary]:
    if current_user.role != "reviewer":
        raise HTTPException(status_code=403, detail="Reviewer role required")

    rows = db.execute(
        select(
            Project.id,
            Project.name,
            Category.name,
            func.count(CompletedVideo.id),
        )
        .outerjoin(Category, Project.category_id == Category.id)
        .outerjoin(Clip, Clip.project_id == Project.id)
        .outerjoin(CompletedVideo, CompletedVideo.clip_id == Clip.id)
        .group_by(Project.id, Project.name, Category.name)
        .order_by(Project.name)
    ).all()

    return [
        ProjectReviewSummary(
            project_id=project_id,
            project_name=project_name,
            category_name=category_name,
            completed_video_count=completed_video_count,
        )
        for project_id, project_name, category_name, completed_video_count in rows
    ]


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/activities/generate", response_model=ActivityIdeasDraft)
async def generate_activities(
    project_id: int,
    payload: ActivityGenerateRequest,
    db: Session = Depends(get_db),
) -> ActivityIdeasDraft:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    theme = db.get(MasterTheme, project.master_theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    try:
        director = AIDirectorService(llm_provider=get_llm_provider())
        return await director.generate_activity_ideas(theme, payload.count)
    except Exception:
        logger.exception("AI Director activity generation failed")
        raise HTTPException(
            status_code=502, detail="AI Director generation failed. Check LLM provider configuration."
        ) from None


@router.post("/{project_id}/clips", response_model=list[ClipRead], status_code=201)
def create_clips(
    project_id: int, payload: ClipsCreateRequest, db: Session = Depends(get_db)
) -> list[Clip]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    clips = [Clip(project_id=project_id, activity=activity) for activity in payload.activities]
    db.add_all(clips)
    db.commit()
    for clip in clips:
        db.refresh(clip)
    return clips


@router.get("/{project_id}/clips", response_model=list[ClipRead])
def list_clips(project_id: int, db: Session = Depends(get_db)) -> list[Clip]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return list(db.scalars(select(Clip).where(Clip.project_id == project_id)).all())


@router.get("/{project_id}/completed-videos", response_model=list[ProjectCompletedVideoRead])
def list_project_completed_videos(
    project_id: int, db: Session = Depends(get_db)
) -> list[ProjectCompletedVideoRead]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = db.execute(
        select(CompletedVideo, Asset, Clip.activity)
        .join(Asset, CompletedVideo.asset_id == Asset.id)
        .join(Clip, CompletedVideo.clip_id == Clip.id)
        .where(Clip.project_id == project_id)
        .order_by(CompletedVideo.created_at.desc())
    ).all()

    return [
        ProjectCompletedVideoRead(
            id=video.id,
            clip_id=video.clip_id,
            asset_id=video.asset_id,
            file_path=asset.file_path,
            mime_type=asset.mime_type,
            created_at=video.created_at,
            clip_activity=activity,
        )
        for video, asset, activity in rows
    ]
