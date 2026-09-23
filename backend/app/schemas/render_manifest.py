from pydantic import BaseModel


class RenderManifest(BaseModel):
    project_id: int
    clip_id: int
    project_name: str
    target_duration: int
    videos: list[str]
    music: list[str]
