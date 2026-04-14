from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator("name")
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    xp: int = 0
    level: int = 1
    streak: int = 0
    badges: List[str] = []


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
