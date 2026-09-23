from datetime import datetime

from pydantic import BaseModel


class CompletedVideoRead(BaseModel):
    id: int
    clip_id: int
    asset_id: int
    file_path: str
    mime_type: str
    created_at: datetime


class ProjectCompletedVideoRead(CompletedVideoRead):
    clip_activity: str
