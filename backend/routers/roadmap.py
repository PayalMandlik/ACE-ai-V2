from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.database import get_database
from backend.core.errors import api_error
from backend.core.security import get_current_user
from schemas.roadmap import RoadmapRequest, RoadmapResponse
from services.roadmap_service import create_roadmap

router = APIRouter()


@router.post("/roadmap", response_model=RoadmapResponse)
async def create_roadmap_route(
    payload: RoadmapRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> RoadmapResponse:
    document = await create_roadmap(db, current_user["_id"], payload.skill, payload.duration_days)
    if document.get("error"):
        raise api_error("roadmap_creation_failed", document.get("message", "Could not create roadmap."), status.HTTP_400_BAD_REQUEST)

    return RoadmapResponse(
        id=document["_id"],
        skill=document["skill"],
        duration_days=document["duration_days"],
        roadmap=document["roadmap"],
        status=document["status"],
    )
