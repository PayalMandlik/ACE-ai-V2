from pydantic import BaseModel, Field


class ResumeAnalyzeRequest(BaseModel):
    text: str | None = None
    source: str = Field(..., min_length=1)


class ResumeAnalyzeResponse(BaseModel):
    id: str
    resume_text: str
    source: str
    analysis: dict
