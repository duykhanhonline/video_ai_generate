from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    activity: str
    status: str
    approved: bool
    image_prompt: str | None
    image_asset_id: int | None
    created_at: datetime
    updated_at: datetime


class ClipsCreateRequest(BaseModel):
    activities: list[str] = Field(min_length=1)


class ImageGenerateRequest(BaseModel):
    force: bool = False
