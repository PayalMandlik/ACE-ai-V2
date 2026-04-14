from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.database import get_database
from backend.core.errors import api_error
from backend.core.security import get_current_user
from schemas.jobs import JobMatchResponse
from services.job_service import match_jobs

router = APIRouter()


@router.get("/jobs", response_model=JobMatchResponse)
async def get_jobs(
    resume_id: str | None = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> JobMatchResponse:
    document = await match_jobs(db, current_user["_id"], resume_id)
    if document.get("error"):
        raise api_error("job_match_failed", document.get("message", "Could not find job matches."), status.HTTP_400_BAD_REQUEST)

    return JobMatchResponse(
        id=document["_id"],
        resume_id=document["resume_id"],
        match_percentage=document["match_percentage"],
        jobs=document["jobs"],
    )
