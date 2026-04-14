from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from schemas.auth import (
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from services.auth_service import (
    authenticate_user,
    create_refresh_token_entry,
    create_user,
    get_refresh_token_entry,
    get_user_by_email,
    get_user_by_id,
    rotate_refresh_token_entry,
)

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: AsyncIOMotorDatabase = Depends(get_database)) -> TokenResponse:
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise api_error("email_already_registered", "Email already registered", status.HTTP_400_BAD_REQUEST)

    user = await create_user(db, payload.name, payload.email, payload.password)
    access_token = create_access_token(subject=user["_id"])
    refresh_token = create_refresh_token(subject=user["_id"])
    await create_refresh_token_entry(db, user["_id"], refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
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
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_database)) -> TokenResponse:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise api_error("invalid_credentials", "Invalid credentials", status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(subject=user["_id"])
    refresh_token = create_refresh_token(subject=user["_id"])
    await create_refresh_token_entry(db, user["_id"], refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    user_id = decode_refresh_token(payload.refresh_token)
    token_entry = await get_refresh_token_entry(db, payload.refresh_token)
    if not token_entry or token_entry.get("user_id") != user_id:
        raise api_error("invalid_refresh_token", "Refresh token is invalid", status.HTTP_401_UNAUTHORIZED)

    user = await get_user_by_id(db, user_id)
    if not user:
        raise api_error("user_not_found", "User not found", status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)
    await rotate_refresh_token_entry(db, payload.refresh_token, refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            xp=user["xp"],
            level=user["level"],
            streak=user["streak"],
            badges=user["badges"],
        ),
    )
