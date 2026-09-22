import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.clip import Clip
from app.models.master_theme import MasterTheme
from app.models.project import Project
from app.providers.registry import get_llm_provider
from app.schemas.ai_director import ActivityGenerateRequest, ActivityIdeasDraft
from app.schemas.clip import ClipRead, ClipsCreateRequest
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.director_service import AIDirectorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    theme = db.get(MasterTheme, payload.master_theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return list(db.scalars(select(Project)).all())


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
