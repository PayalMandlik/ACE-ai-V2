from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.auth_schema import LoginRequest, SignupRequest, TokenResponse, UserResponse
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
)


async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists.",
        )

    user = await create_user(db, payload.name, payload.email, payload.password)
    token = create_access_token(subject=user["_id"])

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["_id"],
            name=user["name"],
            email=user["email"],
            xp=user["xp"],
            level=user["level"],
            streak=user["streak"],
            badges=user["badges"],
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(subject=user["_id"])
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["_id"],
            name=user["name"],
            email=user["email"],
            xp=user.get("xp", 0),
            level=user.get("level", 1),
            streak=user.get("streak", 0),
            badges=user.get("badges", []),
        ),
    )
