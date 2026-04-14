from pydantic import BaseModel, Field


class RoadmapRequest(BaseModel):
    skill: str = Field(..., min_length=1)
    duration_days: int = Field(..., ge=1)


class RoadmapResponse(BaseModel):
    id: str
    skill: str
    duration_days: int
    roadmap: list[dict]
    status: str
