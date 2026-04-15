from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.github_schema import GithubValidateRequest, GithubValidateResponse
from services.github_validation_service import validate_github_repository

router = APIRouter()


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@router.post("/validate/github", response_model=GithubValidateResponse)
async def validate_github(
    payload: GithubValidateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GithubValidateResponse:
    document = await validate_github_repository(db, payload.owner, payload.repo)
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "GitHub validation failed."),
        )

    validation = document["validation"]
    return GithubValidateResponse(
        summary=validation.get("summary", ""),
        skills=validation.get("skills", []),
        score=float(validation.get("score", 0)),
        weaknesses=validation.get("weaknesses", []),
        raw_output=validation.get("raw_output"),
    )
