from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.gap_schema import GapAnalyzeRequest, GapAnalyzeResponse
from services.gap_service import analyze_skill_gap

router = APIRouter()


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@router.post("/analyze", response_model=GapAnalyzeResponse)
async def analyze_gap(
    payload: GapAnalyzeRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> GapAnalyzeResponse:
    # FIX: removed the hard reject on empty resume_skills — skills are optional
    # (user may not have uploaded a resume yet; gap analysis still works against role map)
    result = await analyze_skill_gap(db, payload.target_role, payload.resume_skills)
    return GapAnalyzeResponse(**result)