from pydantic import BaseModel, Field


class GapAnalyzeRequest(BaseModel):
    resume_id: str = Field(..., min_length=1)
    target_role: str = Field(..., min_length=1)


class GapAnalyzeResponse(BaseModel):
    id: str
    resume_id: str
    target_role: str
    expected_skills: list[str]
    resume_skills: list[str]
    matched: list[str]
    missing: list[str]
    priority: list[str]
