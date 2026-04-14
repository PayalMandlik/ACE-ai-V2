from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.gap_schema import GapAnalyzeRequest, GapAnalyzeResponse
from services.gap_service import analyze_skill_gap
from utils.security import get_current_user, get_database

router = APIRouter()


@router.post("/gap/analyze", response_model=GapAnalyzeResponse)
async def analyze_gap(
    payload: GapAnalyzeRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> GapAnalyzeResponse:
    result = await analyze_skill_gap(
        db=db,
        target_role=payload.target_role,
        resume_skills=payload.resume_skills,
        user_id=current_user["_id"],
    )
    return GapAnalyzeResponse(**result)


@router.post("/gap-analysis", response_model=GapAnalyzeResponse)
async def analyze_gap_alias(
    payload: GapAnalyzeRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> GapAnalyzeResponse:
    result = await analyze_skill_gap(
        db=db,
        target_role=payload.target_role,
        resume_skills=payload.resume_skills,
        user_id=current_user["_id"],
    )
    return GapAnalyzeResponse(**result)
