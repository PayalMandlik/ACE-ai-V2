import base64
from datetime import datetime
from typing import Any, Dict, List

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.github_validator import validate_repository

VALIDATIONS_COLLECTION = "validations"
GITHUB_API_BASE = "https://api.github.com"
TIMEOUT_SECONDS = 15.0


async def _fetch_github_readme(owner: str, repo: str) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                return ""
            response.raise_for_status()
            data = response.json()
        content = data.get("content", "")
        encoding = data.get("encoding", "base64")
        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        return content
    except Exception:
        return ""


async def _fetch_github_languages(owner: str, repo: str) -> List[str]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()
        return list(data.keys())
    except Exception:
        return []


async def validate_github_repository(
    db: AsyncIOMotorDatabase,
    owner: str,
    repo: str,
) -> Dict[str, Any]:
    readme_text = await _fetch_github_readme(owner, repo)
    languages = await _fetch_github_languages(owner, repo)

    validation = await validate_repository(readme_text, languages)
    if validation.get("error"):
        return validation

    document: Dict[str, Any] = {
        "owner": owner.strip(),
        "repo": repo.strip(),
        "validation": validation,
    }

    # FIX: wrap DB insert — still return result if MongoDB is unavailable
    try:
        doc = {
            **document,
            "readme": readme_text,
            "languages": languages,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[VALIDATIONS_COLLECTION].insert_one(doc)
        document["_id"] = str(result.inserted_id)
    except Exception:
        pass

    return document