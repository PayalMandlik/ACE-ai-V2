from pydantic import BaseModel, Field


class SuggestionsResponse(BaseModel):
    id: str
    summary: str
    suggestions: list[str]
    priority_actions: list[str]
