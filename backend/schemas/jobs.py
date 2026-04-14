from pydantic import BaseModel, Field


class JobMatchItem(BaseModel):
    title: str
    company: str
    match_percentage: float


class JobMatchResponse(BaseModel):
    id: str
    resume_id: str
    match_percentage: float
    jobs: list[JobMatchItem]
