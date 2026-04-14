from typing import Any, List, Optional

from pydantic import BaseModel, Field


class JobMatchItem(BaseModel):
    title: str
    company: str
    required_score: int
    match_percentage: float


class JobMatchResponse(BaseModel):
    resume_id: Optional[str] = None
    match_percentage: float = Field(..., ge=0, le=100)
    jobs: List[JobMatchItem] = Field(default_factory=list)
    raw_output: Optional[Any] = None
