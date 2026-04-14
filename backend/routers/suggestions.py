from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.database import get_database
from backend.core.errors import api_error
from backend.core.security import get_current_user
from schemas.suggestions import SuggestionsResponse
from services.suggestions_service import create_suggestions

router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    resume_id: str | None = Query(None),
    gap_id: str | None = Query(None),
    validation_id: str | None = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> SuggestionsResponse:
    document = await create_suggestions(db, current_user["_id"], resume_id, gap_id, validation_id)
    if document.get("error"):
        raise api_error("suggestions_creation_failed", document.get("message", "Could not generate suggestions."), status.HTTP_400_BAD_REQUEST)

    return SuggestionsResponse(
        id=document["_id"],
        summary=document["summary"],
        suggestions=document["suggestions"],
        priority_actions=document["priority_actions"],
    )
