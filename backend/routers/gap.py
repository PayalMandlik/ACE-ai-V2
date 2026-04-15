from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import get_current_user
from schemas.gap import GapAnalyzeRequest, GapAnalyzeResponse
from services.gap_service import analyze_gap

router = APIRouter()


@router.post("/analyze", response_model=GapAnalyzeResponse)
async def analyze_gap_route(
    payload: GapAnalyzeRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> GapAnalyzeResponse:
    document = await analyze_gap(db, current_user["_id"], payload.resume_id, payload.target_role)
    if document.get("error"):
        raise api_error("gap_analysis_failed", document.get("message", "Could not analyze gap."), status.HTTP_400_BAD_REQUEST)

    return GapAnalyzeResponse(
        id=document["_id"],
        resume_id=document["resume_id"],
        target_role=document["target_role"],
        expected_skills=document["expected_skills"],
        resume_skills=document["resume_skills"],
        matched=document["matched"],
        missing=document["missing"],
        priority=document["priority"],
    )
