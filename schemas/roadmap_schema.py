from typing import Any, List

from pydantic import BaseModel, Field


class RoadmapItem(BaseModel):
    day: int
    task: str


class RoadmapRequest(BaseModel):
    skill: str = Field(..., min_length=1)
    duration: str = Field(..., min_length=1)


class RoadmapResponse(BaseModel):
    roadmap: List[RoadmapItem] = Field(default_factory=list)
    summary: str
    raw_output: Any = None
