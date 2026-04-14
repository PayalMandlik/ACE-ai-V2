from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import get_current_user
from schemas.assessment import AssessmentCreateResponse, AssessmentSubmitRequest, AssessmentSubmitResponse
from services.assessment_service import generate_assessment, submit_assessment

router = APIRouter()


@router.get("/assessment", response_model=AssessmentCreateResponse)
async def create_assessment(
    skill: str = Query(..., min_length=1),
    roadmap_id: str | None = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> AssessmentCreateResponse:
    document = await generate_assessment(db, current_user["_id"], skill, roadmap_id)
    if document.get("error"):
        raise api_error("assessment_generation_failed", document.get("message", "Could not generate assessment."), status.HTTP_400_BAD_REQUEST)

    return AssessmentCreateResponse(
        assessment_id=document["assessment_id"],
        skill=document["skill"],
        questions=document["questions"],
    )


@router.post("/assessment/submit", response_model=AssessmentSubmitResponse)
async def submit_assessment_route(
    payload: AssessmentSubmitRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> AssessmentSubmitResponse:
    document = await submit_assessment(db, current_user["_id"], payload.assessment_id, payload.answers)
    if document.get("error"):
        raise api_error("assessment_submission_failed", document.get("message", "Could not submit assessment."), status.HTTP_400_BAD_REQUEST)

    return AssessmentSubmitResponse(score=document["score"], feedback=document["feedback"], xp=document["xp"])
