from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job
from app.schemas.job import JobRead, JobUpdate

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "status" in update_data:
        job.status = update_data["status"]
        if job.status in ("COMPLETED", "FAILED") and job.completed_at is None:
            job.completed_at = datetime.now(UTC)

    if "progress" in update_data:
        job.progress = update_data["progress"]

    if "error_message" in update_data:
        job.error_message = update_data["error_message"]

    db.commit()
    db.refresh(job)
    return job
