from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AssessmentQuestion(BaseModel):
    id: str
    question: str
    type: Optional[str] = None
    metadata: Optional[Any] = None


class AssessmentCreateResponse(BaseModel):
    assessment_id: str
    skill: str
    questions: List[AssessmentQuestion]
    raw_output: Optional[Any] = None


class AssessmentSubmitRequest(BaseModel):
    assessment_id: str = Field(..., min_length=1)
    answers: List[dict] = Field(...)


class AssessmentSubmitResponse(BaseModel):
    score: float = Field(..., ge=0, le=100)
    feedback: List[str] = Field(default_factory=list)
    xp: int
    raw_output: Optional[Any] = None
