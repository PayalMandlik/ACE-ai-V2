import asyncio
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.config import settings
from backend.core.database import get_database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _auth_error(code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": code, "message": message})


async def get_password_hash(password: str) -> str:
    hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


async def verify_password(password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(bcrypt.checkpw, password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "access":
            raise _auth_error("invalid_access_token", "Invalid access token")
        subject = payload.get("sub")
        if subject is None:
            raise _auth_error("invalid_access_token", "Could not validate credentials")
        return subject
    except ExpiredSignatureError:
        raise _auth_error("token_expired", "Access token has expired")
    except JWTError:
        raise _auth_error("invalid_token", "Could not validate credentials")


def decode_refresh_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise _auth_error("invalid_refresh_token", "Invalid refresh token")
        subject = payload.get("sub")
        if subject is None:
            raise _auth_error("invalid_refresh_token", "Could not validate refresh token")
        return subject
    except ExpiredSignatureError:
        raise _auth_error("refresh_token_expired", "Refresh token has expired")
    except JWTError:
        raise _auth_error("invalid_refresh_token", "Could not validate refresh token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    user_id = decode_access_token(token)
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise _auth_error("user_not_found", "User not found")

    user = await db["users"].find_one({"_id": object_id})
    if not user:
        raise _auth_error("user_not_found", "User not found")
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user
