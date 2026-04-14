from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SuggestionsResponse(BaseModel):
    summary: str
    focus: List[str] = Field(default_factory=list)
    advice: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    raw_output: Optional[Any] = None
