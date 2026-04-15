from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SuggestionsResponse(BaseModel):
    summary: str
    suggestions: List[str] = Field(default_factory=list)
    priority_actions: List[str] = Field(default_factory=list)
    raw_output: Optional[Any] = None
