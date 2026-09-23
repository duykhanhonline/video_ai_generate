from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    master_theme_id: int
    name: str
    clip_count: int = Field(default=0, ge=0)
    music_count: int = Field(default=0, ge=0)
    target_duration: int = Field(gt=0)
    image_provider: str = "openai"
    video_provider: str = "kling"
    music_provider: str = "manual"
    category_id: int | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    owner_id: int | None
    created_at: datetime
    updated_at: datetime


class ProjectReviewSummary(BaseModel):
    project_id: int
    project_name: str
    category_name: str | None
    completed_video_count: int
