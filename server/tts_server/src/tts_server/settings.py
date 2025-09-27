from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class APISettings(BaseSettings):
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=5502, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    v1_str: str = Field(default="/api", env="API_V1_STR")


class TTSSettings(BaseSettings):
    backend: str = Field(default="piper", env="TTS_BACKEND")  # piper|mimic3|opentts
    base_url: str = Field(default="http://tts-backend:5002", env="TTS_BASE_URL")
    default_voice: str = Field(default="ko_KR-pml_high", env="TTS_DEFAULT_VOICE")


class DBSettings(BaseSettings):
    # align to app_server style when needed
    app_url: str | None = Field(default=None, env="DB_APP_URL")
    pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")


class Settings(BaseSettings):
    app_env: str = Field(default="dev", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    project_name: str = Field(default="TTS Server", env="PROJECT_NAME")
    version: str = Field(default="0.1.0", env="VERSION")

    api: APISettings = APISettings()
    tts: TTSSettings = TTSSettings()
    db: DBSettings = DBSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


