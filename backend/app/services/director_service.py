import json

from app.models.master_theme import MasterTheme
from app.providers.base.llm import LLMProvider
from app.schemas.ai_director import ActivityIdeasDraft, ImagePromptDraft, MasterThemeDraft

SYSTEM_PROMPT = """You are the AI Director for an ambient video production platform.
Your job is to expand a short creative idea into a structured Master Theme.

Rules:
- The Master Theme defines a reusable creative identity: a character, a world, a visual style, and a music style.
- This is NOT a story. There is no plot or narrative arc.
- Favor calm, loop-friendly, ambient visuals: static or slow camera, subtle motion, no dramatic action.
- Keep the character, environment, and mood consistent and specific enough to guide future independent video clips.
"""

MASTER_THEME_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "concept": {"type": "string"},
        "character": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "clothing": {"type": "string"},
            },
            "required": ["description", "clothing"],
            "additionalProperties": False,
        },
        "environment": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "elements": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["location", "elements"],
            "additionalProperties": False,
        },
        "visual_style": {
            "type": "object",
            "properties": {
                "style": {"type": "string"},
                "mood": {"type": "string"},
                "lighting": {"type": "string"},
            },
            "required": ["style", "mood", "lighting"],
            "additionalProperties": False,
        },
        "animation_rules": {
            "type": "object",
            "properties": {
                "movement": {"type": "string"},
                "camera": {"type": "string"},
                "loop_friendly": {"type": "boolean"},
            },
            "required": ["movement", "camera", "loop_friendly"],
            "additionalProperties": False,
        },
        "music_style": {
            "type": "object",
            "properties": {
                "mood": {"type": "string"},
                "instruments": {"type": "array", "items": {"type": "string"}},
                "vocals": {"type": "boolean"},
                "tempo": {"type": "string"},
            },
            "required": ["mood", "instruments", "vocals", "tempo"],
            "additionalProperties": False,
        },
    },
    "required": [
        "name",
        "concept",
        "character",
        "environment",
        "visual_style",
        "animation_rules",
        "music_style",
    ],
    "additionalProperties": False,
}

ACTIVITY_SYSTEM_PROMPT = """You are the AI Director for an ambient video production platform.
Generate a list of independent activity ideas for short ambient video clips based on a Master Theme.

Rules:
- Each activity is simple, calm, and stands alone - it is NOT part of a story or sequence.
- Activities do not need to continue from each other or share any continuity.
- Favor activities compatible with a static or slow camera and subtle, loop-friendly motion
  (e.g. drinking tea, watching rain, meditating) over large or dramatic movement.
- Keep each activity short (a few words) and visually distinct from the others.
"""

ACTIVITY_IDEAS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "activities": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["activities"],
    "additionalProperties": False,
}

IMAGE_PROMPT_SYSTEM_PROMPT = """You are the AI Director for an ambient video production platform.
Generate a single detailed image generation prompt for one video clip's starting frame.

Rules:
- The image must be visually consistent with the Master Theme's character, environment, and visual style.
- Depict the character performing the given activity.
- Favor a calm, ambient composition suitable as the first frame of a slow, loop-friendly video clip:
  static or minimal camera motion implied, no dramatic action, no motion blur.
- Be specific and descriptive (character appearance, clothing, setting, lighting, mood, art style)
  so an image generation model can produce a consistent result.
"""

IMAGE_PROMPT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string"},
    },
    "required": ["prompt"],
    "additionalProperties": False,
}


class AIDirectorService:
    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm_provider = llm_provider

    async def generate_master_theme(self, idea: str) -> MasterThemeDraft:
        user_prompt = f'Expand this idea into a Master Theme: "{idea}"'
        raw = await self._llm_provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_schema=MASTER_THEME_JSON_SCHEMA,
        )
        return MasterThemeDraft.model_validate(raw)

    async def generate_activity_ideas(self, theme: MasterTheme, count: int) -> ActivityIdeasDraft:
        theme_context = {
            "name": theme.name,
            "concept": theme.concept,
            "character": theme.character_json,
            "environment": theme.environment_json,
            "visual_style": theme.visual_style_json,
        }
        user_prompt = (
            f"Master Theme:\n{json.dumps(theme_context, indent=2)}\n\n"
            f"Generate {count} independent activity ideas for this theme."
        )
        raw = await self._llm_provider.generate_structured(
            system_prompt=ACTIVITY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_schema=ACTIVITY_IDEAS_JSON_SCHEMA,
        )
        return ActivityIdeasDraft.model_validate(raw)

    async def generate_image_prompt(self, theme: MasterTheme, activity: str) -> ImagePromptDraft:
        theme_context = {
            "name": theme.name,
            "concept": theme.concept,
            "character": theme.character_json,
            "environment": theme.environment_json,
            "visual_style": theme.visual_style_json,
        }
        user_prompt = (
            f"Master Theme:\n{json.dumps(theme_context, indent=2)}\n\n"
            f'Activity for this clip: "{activity}"\n\n'
            "Generate an image prompt for this clip's starting frame."
        )
        raw = await self._llm_provider.generate_structured(
            system_prompt=IMAGE_PROMPT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_schema=IMAGE_PROMPT_JSON_SCHEMA,
        )
        return ImagePromptDraft.model_validate(raw)
