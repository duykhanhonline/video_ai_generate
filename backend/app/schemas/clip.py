from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ImageRatio = Literal["1024x1024", "1536x1024", "1024x1536"]


class ClipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    activity: str
    status: str
    approved: bool
    image_prompt: str | None
    image_ratio: str
    reference_image_path: str | None
    image_asset_id: int | None
    video_prompt: str | None
    video_asset_id: int | None
    created_at: datetime
    updated_at: datetime


class ClipsCreateRequest(BaseModel):
    activities: list[str] = Field(min_length=1)


class ImageGenerateRequest(BaseModel):
    force: bool = False


class ClipUpdate(BaseModel):
    approved: bool | None = None
    image_prompt: str | None = None
    image_ratio: ImageRatio | None = None
    reference_image_path: str | None = None
    image_asset_id: int | None = None
