from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.suggestions_schema import SuggestionsResponse
from services.suggestion_service import create_suggestions
from utils.security import get_current_user, get_database

router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    resume_id: Optional[str] = Query(None),
    gap_id: Optional[str] = Query(None),
    validation_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> SuggestionsResponse:
    document = await create_suggestions(
        db,
        resume_id=resume_id,
        gap_id=gap_id,
        validation_id=validation_id,
        user_id=current_user["_id"],
    )
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Suggestions generation failed."),
        )

    return SuggestionsResponse(
        summary=document.get("summary", ""),
        focus=document.get("focus", []),
        advice=document.get("advice", []),
        avoid=document.get("avoid", []),
        raw_output=document.get("raw_output"),
    )
