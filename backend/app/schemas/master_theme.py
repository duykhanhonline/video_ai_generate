from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class MasterThemeBase(BaseModel):
    name: str
    concept: str
    character_json: dict[str, Any] | None = None
    environment_json: dict[str, Any] | None = None
    visual_style_json: dict[str, Any] | None = None
    animation_rules_json: dict[str, Any] | None = None
    music_style_json: dict[str, Any] | None = None
    reference_image: str | None = None


class MasterThemeCreate(MasterThemeBase):
    pass


class MasterThemeUpdate(BaseModel):
    name: str | None = None
    concept: str | None = None
    character_json: dict[str, Any] | None = None
    environment_json: dict[str, Any] | None = None
    visual_style_json: dict[str, Any] | None = None
    animation_rules_json: dict[str, Any] | None = None
    music_style_json: dict[str, Any] | None = None
    reference_image: str | None = None


class MasterThemeRead(MasterThemeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int | None
    created_at: datetime
    updated_at: datetime
