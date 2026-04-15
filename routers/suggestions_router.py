from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.suggestions_schema import SuggestionsResponse
from services.suggestion_service import create_suggestions

router = APIRouter()


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    resume_id: Optional[str] = Query(None),
    gap_id: Optional[str] = Query(None),
    validation_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SuggestionsResponse:
    document = await create_suggestions(db, resume_id, gap_id, validation_id)
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Failed to generate suggestions."),
        )

    return SuggestionsResponse(
        summary=document.get("summary", ""),
        suggestions=document.get("suggestions", []),
        priority_actions=document.get("priority_actions", []),
        raw_output=document.get("raw_output"),
    )
