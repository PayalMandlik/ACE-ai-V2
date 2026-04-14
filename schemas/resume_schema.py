from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ResumeAnalyzeResponse(BaseModel):
    score: float = Field(..., ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    raw_output: Optional[Any] = None
