from datetime import datetime

from pydantic import BaseModel


class MusicTrackRead(BaseModel):
    id: int
    project_id: int
    title: str
    asset_id: int
    file_path: str
    mime_type: str
    approved: bool
    created_at: datetime
    updated_at: datetime
