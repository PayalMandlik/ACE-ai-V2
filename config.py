import secrets
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


def _generate_secret() -> str:
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    # This handles the 'gemini_api_key' error you saw earlier
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    GITHUB_TOKEN: str | None = Field(None, env="GITHUB_TOKEN")

    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db: str = Field("ace_ai", env="MONGODB_DB")
    secret_key: str = Field(default_factory=_generate_secret, env="SECRET_KEY")
    debug: bool = Field(True, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Stops the app from crashing if .env has extra keys

settings = Settings()