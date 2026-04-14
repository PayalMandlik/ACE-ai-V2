import logging
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core.security import get_password_hash, verify_password

logger = logging.getLogger("ace_ai")
USERS_COLLECTION = "users"
REFRESH_TOKENS_COLLECTION = "refresh_tokens"


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    try:
        return await db[USERS_COLLECTION].find_one({"email": normalize_email(email)})
    except Exception as exc:
        logger.error("Failed to load user by email", exc_info=exc)
        return None


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    try:
        object_id = ObjectId(user_id)
    except Exception:
        return None
    try:
        return await db[USERS_COLLECTION].find_one({"_id": object_id})
    except Exception as exc:
        logger.error("Failed to load user by id", exc_info=exc)
        return None


async def create_user(db: AsyncIOMotorDatabase, name: str, email: str, password: str) -> dict:
    try:
        user_data = {
            "name": name.strip(),
            "email": normalize_email(email),
            "password": await get_password_hash(password),
            "xp": 0,
            "level": 1,
            "streak": 0,
            "badges": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[USERS_COLLECTION].insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        user_data.pop("password", None)
        logger.info("Created new user", extra={"user_id": user_data["_id"], "email": user_data["email"]})
        return user_data
    except DuplicateKeyError as exc:
        logger.warning("Duplicate email during user creation", exc_info=exc, extra={"email": normalize_email(email)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "email_already_registered", "message": "Email already registered."},
        )
    except Exception as exc:
        logger.error("Error creating user", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "database_error", "message": "Could not create user."},
        )


async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[dict]:
    try:
        user = await get_user_by_email(db, email)
    except Exception as exc:
        logger.error("Failed to authenticate user", exc_info=exc, extra={"email": email})
        return None
    if not user:
        return None
    if not await verify_password(password, user.get("password", "")):
        return None
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user


async def create_refresh_token_entry(db: AsyncIOMotorDatabase, user_id: str, token: str) -> dict:
    document = {
        "user_id": user_id,
        "token": token,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[REFRESH_TOKENS_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    logger.info("Created refresh token", extra={"user_id": user_id})
    return document


async def get_refresh_token_entry(db: AsyncIOMotorDatabase, token: str) -> Optional[dict]:
    try:
        return await db[REFRESH_TOKENS_COLLECTION].find_one({"token": token})
    except Exception as exc:
        logger.error("Failed to load refresh token", exc_info=exc)
        return None


async def rotate_refresh_token_entry(db: AsyncIOMotorDatabase, old_token: str, new_token: str) -> Optional[dict]:
    try:
        result = await db[REFRESH_TOKENS_COLLECTION].find_one_and_update(
            {"token": old_token},
            {"$set": {"token": new_token, "updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            logger.info("Rotated refresh token", extra={"user_id": result.get("user_id")})
        return result
    except Exception as exc:
        logger.error("Failed to rotate refresh token", exc_info=exc)
        return None
