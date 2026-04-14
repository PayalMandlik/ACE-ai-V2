import base64
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.github_validator import validate_repository
from config import settings

VALIDATIONS_COLLECTION = "validations"
GITHUB_API_BASE = "https://api.github.com"
TIMEOUT_SECONDS = 10.0


async def _fetch_github_readme(owner: str, repo: str) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                return ""
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return f"Error fetching README: {str(exc)}"

    content = data.get("content", "")
    encoding = data.get("encoding", "base64")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="ignore")
    return content


async def _fetch_github_languages(owner: str, repo: str) -> List[str]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return []

    return list(data.keys())


async def validate_github_repository(
    db: AsyncIOMotorDatabase,
    owner: str,
    repo: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    readme_text = await _fetch_github_readme(owner, repo)
    if readme_text.startswith("Error fetching README:"):
        return {"error": "github_fetch_error", "message": readme_text}

    languages = await _fetch_github_languages(owner, repo)
    validation = await validate_repository(readme_text, languages)

    if validation.get("error"):
        return validation

    document: Dict[str, Any] = {
        "owner": owner.strip(),
        "repo": repo.strip(),
        "readme": readme_text,
        "languages": languages,
        "validation": validation,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[VALIDATIONS_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
