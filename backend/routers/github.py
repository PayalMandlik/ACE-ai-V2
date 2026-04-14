from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import get_current_user
from schemas.github import GithubValidateRequest, GithubValidateResponse
from services.github_service import validate_github_repo

router = APIRouter()


@router.post("/validate/github", response_model=GithubValidateResponse)
async def validate_github(
    payload: GithubValidateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> GithubValidateResponse:
    document = await validate_github_repo(db, current_user["_id"], str(payload.repo_url))
    if document.get("error"):
        raise api_error("github_validation_failed", document.get("message", "Could not validate repository."), status.HTTP_400_BAD_REQUEST)

    return GithubValidateResponse(
        id=document["_id"],
        repo_url=document["repo_url"],
        owner=document["owner"],
        repo=document["repo"],
        languages=document["languages"],
        validation=document["validation"],
    )
