from typing import List

from pydantic import BaseModel, Field


class GapAnalyzeRequest(BaseModel):
    target_role: str = Field(..., min_length=1)
    resume_skills: List[str] = Field(default_factory=list)


class GapAnalyzeResponse(BaseModel):
    matched: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)
    priority: List[str] = Field(default_factory=list)
