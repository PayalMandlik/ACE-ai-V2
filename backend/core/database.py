import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import settings

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

    validators = {
        "users": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "email", "password", "xp", "level", "streak", "badges", "created_at", "updated_at"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "password": {"bsonType": "string"},
                    "xp": {"bsonType": "int"},
                    "level": {"bsonType": "int"},
                    "streak": {"bsonType": "int"},
                    "badges": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "resumes": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "resume_text", "analysis", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "resume_text": {"bsonType": "string"},
                    "analysis": {
                        "bsonType": "object",
                        "required": ["score", "strengths", "weaknesses", "missing_skills", "keywords"],
                        "properties": {
                            "score": {"bsonType": ["double", "int"]},
                            "strengths": {"bsonType": "array"},
                            "weaknesses": {"bsonType": "array"},
                            "missing_skills": {"bsonType": "array"},
                            "keywords": {"bsonType": "array"},
                        },
                    },
                    "source": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "gap_analysis": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "resume_id", "target_role", "expected_skills", "resume_skills", "matched", "missing", "priority", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "resume_id": {"bsonType": "string"},
                    "target_role": {"bsonType": "string"},
                    "expected_skills": {"bsonType": "array"},
                    "resume_skills": {"bsonType": "array"},
                    "matched": {"bsonType": "array"},
                    "missing": {"bsonType": "array"},
                    "priority": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "validations": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "repo_url", "owner", "repo", "readme", "languages", "validation", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "repo_url": {"bsonType": "string"},
                    "owner": {"bsonType": "string"},
                    "repo": {"bsonType": "string"},
                    "readme": {"bsonType": "string"},
                    "languages": {"bsonType": "array"},
                    "validation": {
                        "bsonType": "object",
                        "required": ["summary", "skills", "score", "weaknesses"],
                        "properties": {
                            "summary": {"bsonType": "string"},
                            "skills": {"bsonType": "array"},
                            "score": {"bsonType": ["double", "int"]},
                            "weaknesses": {"bsonType": "array"},
                        },
                    },
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "roadmaps": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "skill", "duration_days", "roadmap", "status", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "skill": {"bsonType": "string"},
                    "duration_days": {"bsonType": "int"},
                    "roadmap": {"bsonType": "array"},
                    "status": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "assessments": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "assessment_id", "skill", "questions", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "assessment_id": {"bsonType": "string"},
                    "skill": {"bsonType": "string"},
                    "questions": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "suggestions": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "summary", "suggestions", "priority_actions", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "resume_id": {"bsonType": ["string", "null"]},
                    "gap_id": {"bsonType": ["string", "null"]},
                    "validation_id": {"bsonType": ["string", "null"]},
                    "summary": {"bsonType": "string"},
                    "suggestions": {"bsonType": "array"},
                    "priority_actions": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "jobs": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "resume_id", "match_percentage", "jobs", "created_at", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "resume_id": {"bsonType": "string"},
                    "match_percentage": {"bsonType": ["double", "int"]},
                    "jobs": {"bsonType": "array"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "progress": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "roadmap_id", "completed_days", "current_day", "updated_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "roadmap_id": {"bsonType": "string"},
                    "skill": {"bsonType": "string"},
                    "completed_days": {"bsonType": "int"},
                    "current_day": {"bsonType": "int"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            }
        },
        "refresh_tokens": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "token", "created_at", "updated_at", "expires_at"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "token": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                    "expires_at": {"bsonType": "date"},
                },
            }
        },
    }

    for name, validator in validators.items():
        await _ensure_collection_validator(db, name, validator)

    await db["users"].create_index("email", unique=True)
    await db["resumes"].create_index([("user_id", 1), ("created_at", -1)])
    await db["gap_analysis"].create_index([("user_id", 1), ("resume_id", 1)])
    await db["validations"].create_index([("user_id", 1), ("created_at", -1)])
    await db["roadmaps"].create_index([("user_id", 1), ("created_at", -1)])
    await db["assessments"].create_index([("user_id", 1), ("created_at", -1)])
    await db["suggestions"].create_index([("user_id", 1), ("created_at", -1)])
    await db["jobs"].create_index([("user_id", 1), ("created_at", -1)])
    await db["progress"].create_index([("user_id", 1), ("roadmap_id", 1)], unique=True)
    await db["refresh_tokens"].create_index("token", unique=True)
    await db["refresh_tokens"].create_index([("expires_at", 1)], expireAfterSeconds=0)


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
