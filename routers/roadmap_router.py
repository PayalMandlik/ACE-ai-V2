from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.roadmap_schema import RoadmapRequest, RoadmapResponse
from services.roadmap_service import create_roadmap

router = APIRouter()


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


@router.post("/roadmap", response_model=RoadmapResponse)
async def create_roadmap_route(
    payload: RoadmapRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> RoadmapResponse:
    document = await create_roadmap(db, payload.skill, payload.duration)
    if document.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=document.get("message", "Roadmap generation failed."),
        )

    return RoadmapResponse(
        summary=document.get("summary", ""),
        roadmap=document.get("roadmap", []),
        raw_output=document.get("raw_output"),
    )
