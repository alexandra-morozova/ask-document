from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str
    openai_api_key: str
    allowed_origins: Annotated[list[str], NoDecode]
    allowed_email_domain: str | None = None
    openai_embedding_model: str
    openai_embedding_dimensions: int

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("allowed_email_domain", mode="before")
    @classmethod
    def normalize_email_domain(cls, value: object) -> object:
        if value is None or value == "":
            return None
        if isinstance(value, str):
            domain = value.strip().lstrip("@").lower()
            return domain or None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
