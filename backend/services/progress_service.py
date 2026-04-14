import logging
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("ace_ai")
PROGRESS_COLLECTION = "progress"
ROADMAPS_COLLECTION = "roadmaps"


async def get_progress(db: AsyncIOMotorDatabase, user_id: str, roadmap_id: str) -> Optional[Dict[str, Any]]:
    try:
        return await db[PROGRESS_COLLECTION].find_one({"user_id": user_id, "roadmap_id": roadmap_id})
    except Exception as exc:
        logger.error("Failed to get progress", exc_info=exc, extra={"user_id": user_id, "roadmap_id": roadmap_id})
        return None


async def _resolve_skill(db: AsyncIOMotorDatabase, user_id: str, roadmap_id: str) -> str:
    try:
        roadmap_object_id = ObjectId(roadmap_id)
    except Exception:
        return ""
    roadmap = await db[ROADMAPS_COLLECTION].find_one({"_id": roadmap_object_id, "user_id": user_id})
    return roadmap.get("skill", "") if roadmap else ""


async def create_or_update_progress(
    db: AsyncIOMotorDatabase,
    user_id: str,
    roadmap_id: str,
    skill: str | None,
    completed_days: int,
    current_day: int,
) -> Dict[str, Any]:
    try:
        if not skill:
            skill = await _resolve_skill(db, user_id, roadmap_id)

        existing = await db[PROGRESS_COLLECTION].find_one({"user_id": user_id, "roadmap_id": roadmap_id})
        document = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "skill": skill,
            "completed_days": completed_days,
            "current_day": current_day,
            "updated_at": datetime.utcnow(),
        }
        if existing:
            await db[PROGRESS_COLLECTION].update_one({"_id": existing["_id"]}, {"$set": document})
            existing.update(document)
            existing["_id"] = str(existing["_id"])
            logger.info("Updated progress", extra={"user_id": user_id, "roadmap_id": roadmap_id})
            return existing

        document["created_at"] = datetime.utcnow()
        result = await db[PROGRESS_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        logger.info("Created progress", extra={"user_id": user_id, "roadmap_id": roadmap_id})
        return document
    except Exception as exc:
        logger.error("Failed to create or update progress", exc_info=exc, extra={"user_id": user_id, "roadmap_id": roadmap_id})
        return {"error": "database_error", "message": "Could not save progress."}
