import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

# Load environment variables from .env in the project root.
_load_dotenv(Path(__file__).resolve().parent / ".env")


def _bool_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y")


class Settings:
    mongodb_uri: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.environ.get("MONGODB_DB", "ace_ai")
    secret_key: str = os.environ.get("SECRET_KEY", "change-me")
    debug: bool = _bool_env(os.environ.get("DEBUG"), True)
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")


settings = Settings()
