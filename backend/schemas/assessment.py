from pydantic import BaseModel, Field


class AssessmentCreateResponse(BaseModel):
    assessment_id: str
    skill: str
    questions: list[dict]


class AssessmentSubmitRequest(BaseModel):
    assessment_id: str = Field(..., min_length=1)
    answers: list[dict]


class AssessmentSubmitResponse(BaseModel):
    score: float
    feedback: list[str]
    xp: int
