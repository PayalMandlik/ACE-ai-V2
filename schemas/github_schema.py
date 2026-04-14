from typing import Any, List, Optional

from pydantic import BaseModel, Field


class GithubValidateRequest(BaseModel):
    owner: Optional[str] = Field(None)
    repo: Optional[str] = Field(None)
    url: Optional[str] = Field(None)


class GithubValidateResponse(BaseModel):
    summary: str
    skills_detected: List[str] = Field(default_factory=list)
    score: float = Field(..., ge=0, le=100)
    weaknesses: List[str] = Field(default_factory=list)
    raw_output: Optional[Any] = None
