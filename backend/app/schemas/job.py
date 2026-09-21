from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
