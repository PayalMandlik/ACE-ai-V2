from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
USERS_COLLECTION = "users"


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    return await db[USERS_COLLECTION].find_one({"email": email.lower()})


async def create_user(db: AsyncIOMotorDatabase, name: str, email: str, password: str) -> dict:
    user_data = {
        "name": name.strip(),
        "email": email.lower(),
        "password": hash_password(password),
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
    return user_data


async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> Optional[dict]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.get("password", "")):
        return None
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    return user


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
