from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    clip_id: int | None
    asset_type: str
    provider: str
    provider_model: str
    file_path: str
    mime_type: str
    metadata_json: dict[str, Any] | None
    created_at: datetime
