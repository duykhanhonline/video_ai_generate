from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"

    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_database: str = "ambient_video"
    mysql_user: str = "ambient"
    mysql_password: str = ""

    redis_url: str = "redis://redis:6379/0"

    media_root: str = "/data"

    llm_provider: str = "openai"
    openai_api_key: str = ""

    jwt_secret: str = "dev-secret-change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
