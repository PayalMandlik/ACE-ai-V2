from fastapi import APIRouter, Depends, Path, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import get_current_user
from schemas.progress import ProgressResponse, ProgressUpdateRequest
from services.progress_service import create_or_update_progress, get_progress

router = APIRouter()


@router.get("/{roadmap_id}", response_model=ProgressResponse)
async def get_progress_route(
    roadmap_id: str = Path(..., min_length=1),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    document = await get_progress(db, current_user["_id"], roadmap_id)
    if not document:
        raise api_error("progress_not_found", "Progress not found.", status.HTTP_404_NOT_FOUND)

    return ProgressResponse(
        id=str(document["_id"]),
        roadmap_id=document["roadmap_id"],
        skill=document["skill"],
        completed_days=document["completed_days"],
        current_day=document["current_day"],
    )


@router.post("/update", response_model=ProgressResponse)
async def update_progress(
    payload: ProgressUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    document = await create_or_update_progress(
        db,
        current_user["_id"],
        payload.roadmap_id,
        None,
        payload.completed_days,
        payload.current_day,
    )
    if document.get("error"):
        raise api_error("progress_update_failed", document.get("message", "Could not update progress."), status.HTTP_400_BAD_REQUEST)
    return ProgressResponse(
        id=document["_id"],
        roadmap_id=document["roadmap_id"],
        skill=document["skill"],
        completed_days=document["completed_days"],
        current_day=document["current_day"],
    )
