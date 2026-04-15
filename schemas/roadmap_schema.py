from typing import Any, List

from pydantic import BaseModel, Field


class RoadmapRequest(BaseModel):
    skill: str = Field(..., min_length=1)
    duration: str = Field(..., min_length=1)


class RoadmapResponse(BaseModel):
    roadmap: List[str] = Field(default_factory=list)
    summary: str
    raw_output: Any
