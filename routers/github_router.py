from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.github_schema import GithubValidateRequest, GithubValidateResponse
from services.github_validation_service import validate_github_repository
from utils.security import get_current_user, get_database

router = APIRouter()


def _parse_github_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    path_parts = [segment for segment in parsed.path.split("/") if segment]
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")
    return path_parts[0], path_parts[1]


@router.post("/validate/github", response_model=GithubValidateResponse)
async def validate_github(
    payload: GithubValidateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> GithubValidateResponse:
    owner = payload.owner
    repo = payload.repo
    if not owner or not repo:
        if payload.url:
            try:
                owner, repo = _parse_github_url(payload.url)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(exc),
                )

    if not owner or not repo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A GitHub owner and repository name are required.",
        )

    document = await validate_github_repository(db, owner, repo, user_id=current_user["_id"])
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "GitHub validation failed."),
        )

    validation = document["validation"]
    return GithubValidateResponse(
        summary=validation.get("summary", ""),
        skills_detected=validation.get("skills", []),
        score=float(validation.get("score", 0)),
        weaknesses=validation.get("weaknesses", []),
        raw_output=validation.get("raw_output"),
    )
