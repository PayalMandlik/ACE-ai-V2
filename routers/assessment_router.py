from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.assessment_schema import (
    AssessmentCreateResponse,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
)
from services.assessment_service import create_assessment, submit_assessment
from utils.security import get_current_user, get_database

router = APIRouter()


@router.get("/assessment", response_model=AssessmentCreateResponse)
async def get_assessment(
    skill: str = Query(..., min_length=1),
    num_questions: Optional[int] = Query(5, ge=1, le=10),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> AssessmentCreateResponse:
    document = await create_assessment(db, skill, num_questions, current_user["_id"])
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Failed to generate assessment."),
        )

    return AssessmentCreateResponse(
        assessment_id=document["assessment_id"],
        skill=document["skill"],
        questions=document["questions"],
        raw_output=document.get("raw_output"),
    )


@router.post("/assessment/submit", response_model=AssessmentSubmitResponse)
async def submit_assessment_route(
    payload: AssessmentSubmitRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> AssessmentSubmitResponse:
    document = await submit_assessment(db, current_user["_id"], payload.assessment_id, payload.answers)
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if document["error"] == "not_found" else status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Failed to submit assessment."),
        )

    return AssessmentSubmitResponse(
        score=document["score"],
        feedback=document.get("feedback", []),
        xp=document.get("xp", 0),
        raw_output=document.get("raw_output"),
    )
