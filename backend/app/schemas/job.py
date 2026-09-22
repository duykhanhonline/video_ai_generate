from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

JobStatus = Literal["PENDING", "RUNNING", "WAITING_PROVIDER", "COMPLETED", "FAILED", "CANCELLED"]


class JobUpdate(BaseModel):
    status: JobStatus | None = None
    progress: int | None = None
    error_message: str | None = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    clip_id: int | None
    job_type: str
    provider: str
    external_job_id: str | None
    status: str
    progress: int
    error_message: str | None
    retry_count: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
