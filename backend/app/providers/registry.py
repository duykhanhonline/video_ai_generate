from app.core.config import get_settings
from app.providers.base.image import ImageProvider
from app.providers.base.llm import LLMProvider
from app.providers.image.openai import OpenAIImageProvider
from app.providers.llm.openai import OpenAIProvider

_LLM_PROVIDERS: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
}

_IMAGE_PROVIDERS: dict[str, type[ImageProvider]] = {
    "openai": OpenAIImageProvider,
}


def get_llm_provider(name: str | None = None) -> LLMProvider:
    provider_name = name or get_settings().llm_provider
    provider_cls = _LLM_PROVIDERS.get(provider_name)
    if provider_cls is None:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return provider_cls()


def get_image_provider(name: str) -> ImageProvider:
    provider_cls = _IMAGE_PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(f"Unknown image provider: {name}")
    return provider_cls()
