import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.core.config import settings
from backend.core.db_schema import COLLECTION_VALIDATORS, INDEX_DEFINITIONS

logger = logging.getLogger("ace_ai")

client: Optional[AsyncIOMotorClient] = None

db: Optional[AsyncIOMotorDatabase] = None


async def _ensure_collection_validator(db: AsyncIOMotorDatabase, name: str, validator: dict) -> None:
    existing = await db.list_collection_names()
    if name not in existing:
        await db.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
    else:
        await db.command({"collMod": name, "validator": validator, "validationLevel": "strict", "validationAction": "error"})


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    logger.info("Creating MongoDB indexes and validators")

    for name, validator in COLLECTION_VALIDATORS.items():
        await _ensure_collection_validator(db, name, validator)

    for collection_name, indexes in INDEX_DEFINITIONS.items():
        for index in indexes:
            keys = index["keys"]
            options = index.get("options", {})
            await db[collection_name].create_index(keys, **options)


async def connect_to_mongo() -> None:
    global client, db
    try:
        client = AsyncIOMotorClient(
            settings.mongodb_uri,
            minPoolSize=settings.mongodb_min_pool_size,
            maxPoolSize=settings.mongodb_max_pool_size,
            serverSelectionTimeoutMS=5000,
        )
        db = client[settings.mongodb_db]
        await create_indexes(db)
        await db.command({"ping": 1})
        logger.info("Connected to MongoDB", extra={"database": settings.mongodb_db})
    except Exception as exc:
        logger.error("MongoDB connection failed", exc_info=exc)
        raise


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()
        logger.info("Closed MongoDB connection")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    return db
