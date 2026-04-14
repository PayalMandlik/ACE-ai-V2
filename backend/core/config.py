from typing import List

from pydantic_settings import BaseSettings
from pydantic_settings import Field

class Settings(BaseSettings):
    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db: str = Field("ace_ai", env="MONGODB_DB")
    secret_key: str = Field("change-this-secret-key", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    mongodb_min_pool_size: int = Field(1, env="MONGODB_MIN_POOL_SIZE")
    mongodb_max_pool_size: int = Field(10, env="MONGODB_MAX_POOL_SIZE")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ORIGINS")
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_seconds: int = Field(60, env="RATE_LIMIT_SECONDS")
    max_upload_size_bytes: int = Field(1048576, env="MAX_UPLOAD_SIZE_BYTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
