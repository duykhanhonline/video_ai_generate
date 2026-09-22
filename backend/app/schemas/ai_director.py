from pydantic import BaseModel, ConfigDict, Field


class CharacterProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: str
    clothing: str


class EnvironmentProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    location: str
    elements: list[str]


class VisualStyleProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    style: str
    mood: str
    lighting: str


class AnimationRulesProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    movement: str
    camera: str
    loop_friendly: bool


class MusicStyleProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    mood: str
    instruments: list[str]
    vocals: bool
    tempo: str


class MasterThemeDraft(BaseModel):
    name: str
    concept: str
    character: CharacterProfile
    environment: EnvironmentProfile
    visual_style: VisualStyleProfile
    animation_rules: AnimationRulesProfile
    music_style: MusicStyleProfile


class MasterThemeGenerateRequest(BaseModel):
    idea: str


class ActivityIdeasDraft(BaseModel):
    activities: list[str]


class ActivityGenerateRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=50)


class ImagePromptDraft(BaseModel):
    prompt: str


class VideoPromptDraft(BaseModel):
    prompt: str
