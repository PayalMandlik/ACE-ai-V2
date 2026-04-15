from typing import Any, List, Optional

from pydantic import BaseModel, Field


class GithubValidateRequest(BaseModel):
    owner: str = Field(..., min_length=1)
    repo: str = Field(..., min_length=1)


class GithubValidateResponse(BaseModel):
    summary: str
    skills: List[str] = Field(default_factory=list)
    score: float = Field(..., ge=0, le=100)
    weaknesses: List[str] = Field(default_factory=list)
    raw_output: Optional[Any] = None
