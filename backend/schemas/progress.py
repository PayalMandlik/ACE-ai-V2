from pydantic import BaseModel, Field


class ProgressUpdateRequest(BaseModel):
    roadmap_id: str = Field(..., min_length=1)
    completed_days: int = Field(..., ge=0)
    current_day: int = Field(..., ge=0)


class ProgressResponse(BaseModel):
    id: str
    roadmap_id: str
    skill: str
    completed_days: int
    current_day: int
