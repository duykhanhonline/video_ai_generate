from typing import Any

import pytest
from pydantic import ValidationError

from app.models.master_theme import MasterTheme
from app.providers.base.llm import LLMProvider
from app.services.director_service import AIDirectorService

VALID_RESPONSE: dict[str, Any] = {
    "name": "Mountain Wizard",
    "concept": "A lonely wizard living in a mountain tower.",
    "character": {"description": "An old wizard", "clothing": "grey robes"},
    "environment": {
        "location": "mountain tower",
        "elements": ["fog", "stone", "candlelight"],
    },
    "visual_style": {
        "style": "painterly fantasy",
        "mood": "mysterious",
        "lighting": "warm candlelight",
    },
    "animation_rules": {"movement": "slow", "camera": "static", "loop_friendly": True},
    "music_style": {
        "mood": "mystical",
        "instruments": ["strings", "choir"],
        "vocals": False,
        "tempo": "60-80 BPM",
    },
}


class FakeLLMProvider(LLMProvider):
    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_name(self) -> str:
        return "fake-model"

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, json_schema: dict[str, Any]
    ) -> dict[str, Any]:
        return self._response


async def test_generate_master_theme_returns_validated_draft() -> None:
    director = AIDirectorService(llm_provider=FakeLLMProvider(VALID_RESPONSE))

    draft = await director.generate_master_theme("A lonely wizard living in a mountain tower.")

    assert draft.name == "Mountain Wizard"
    assert draft.character.description == "An old wizard"
    assert draft.animation_rules.loop_friendly is True
    assert draft.music_style.instruments == ["strings", "choir"]


async def test_generate_master_theme_rejects_incomplete_response() -> None:
    invalid_response = {k: v for k, v in VALID_RESPONSE.items() if k != "character"}
    director = AIDirectorService(llm_provider=FakeLLMProvider(invalid_response))

    with pytest.raises(ValidationError):
        await director.generate_master_theme("idea")


async def test_generate_activity_ideas_returns_validated_list() -> None:
    provider = FakeLLMProvider({"activities": ["Drinking tea", "Watching rain", "Meditating"]})
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    result = await director.generate_activity_ideas(theme, count=3)

    assert result.activities == ["Drinking tea", "Watching rain", "Meditating"]


async def test_generate_activity_ideas_rejects_invalid_response() -> None:
    provider = FakeLLMProvider({"activities": "not-a-list"})
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    with pytest.raises(ValidationError):
        await director.generate_activity_ideas(theme, count=3)


async def test_generate_image_prompt_returns_validated_prompt() -> None:
    provider = FakeLLMProvider({"prompt": "A calm samurai drinking tea on a wooden porch."})
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    result = await director.generate_image_prompt(theme, "Drinking tea")

    assert result.prompt == "A calm samurai drinking tea on a wooden porch."


async def test_generate_image_prompt_rejects_invalid_response() -> None:
    provider = FakeLLMProvider({"prompt": 12345})
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    with pytest.raises(ValidationError):
        await director.generate_image_prompt(theme, "Drinking tea")


async def test_generate_video_prompt_returns_validated_prompt() -> None:
    provider = FakeLLMProvider(
        {"prompt": "Steam gently rises from the tea as the samurai's kimono sways slightly."}
    )
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    result = await director.generate_video_prompt(
        theme, "Drinking tea", "A calm samurai drinking tea on a wooden porch."
    )

    assert result.prompt == "Steam gently rises from the tea as the samurai's kimono sways slightly."


async def test_generate_video_prompt_rejects_invalid_response() -> None:
    provider = FakeLLMProvider({"prompt": None})
    director = AIDirectorService(llm_provider=provider)
    theme = MasterTheme(name="Lone Samurai", concept="A solitary samurai in rural Japan.")

    with pytest.raises(ValidationError):
        await director.generate_video_prompt(theme, "Drinking tea", "A calm samurai drinking tea.")
