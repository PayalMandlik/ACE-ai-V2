from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.job_schema import JobMatchResponse
from services.job_service import match_jobs

router = APIRouter()


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@router.get("/jobs", response_model=JobMatchResponse)
async def get_jobs(
    resume_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> JobMatchResponse:
    document = await match_jobs(db, resume_id)
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if document["error"] == "resume_not_found" else status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Job matching failed."),
        )

    return JobMatchResponse(
        resume_id=document.get("resume_id"),
        match_percentage=float(document.get("match_percentage", 0.0)),
        jobs=document.get("jobs", []),
        raw_output=document.get("raw_output"),
    )
