import base64
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.github_validator import validate_repository

VALIDATIONS_COLLECTION = "validations"
GITHUB_API_BASE = "https://api.github.com"
TIMEOUT_SECONDS = 10.0
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


def _build_headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


async def _check_repo_exists(owner: str, repo: str) -> bool:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        response = await client.get(url, headers=_build_headers())
        if response.status_code == 404:
            return False
        response.raise_for_status()
    return True


async def _fetch_github_readme(owner: str, repo: str) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
    headers = _build_headers()

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


async def _fetch_github_languages(owner: str, repo: str) -> List[str]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
    headers = _build_headers()

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()

    return list(data.keys())


async def validate_github_repository(
    db: AsyncIOMotorDatabase,
    owner: str,
    repo: str,
) -> Dict[str, Any]:
    try:
        if not await _check_repo_exists(owner, repo):
            return {
                "error": "repo_not_found",
                "message": "GitHub repository not found. Check owner and repo values.",
            }

        readme_text = await _fetch_github_readme(owner, repo)
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[VALIDATIONS_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = f"GitHub API error {status_code}: {exc.response.text or exc.response.reason_phrase}"
        return {"error": "github_api_error", "message": message}
    except Exception as exc:
        return {"error": "github_error", "message": f"GitHub validation failed: {exc}"}
