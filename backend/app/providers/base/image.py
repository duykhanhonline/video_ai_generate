from abc import ABC, abstractmethod


class ImageProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        reference_images: list[str] | None = None,
    ) -> str:
        raise NotImplementedError
