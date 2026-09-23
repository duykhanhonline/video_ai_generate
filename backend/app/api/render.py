from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job
from app.models.project import Project
from app.schemas.job import JobRead

router = APIRouter(prefix="/api/projects", tags=["render"])


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
