import logging
from datetime import datetime
from typing import Any, Dict

from agents.roadmap_agent import generate_roadmap
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("ace_ai")
ROADMAPS_COLLECTION = "roadmaps"


async def create_roadmap(db: AsyncIOMotorDatabase, user_id: str, skill: str, duration_days: int) -> Dict[str, Any]:
    try:
        roadmap_data = await generate_roadmap(skill, duration_days)
        if roadmap_data.get("error"):
            return roadmap_data

        document = {
            "user_id": user_id,
            "skill": skill.strip(),
            "duration_days": duration_days,
            "roadmap": roadmap_data.get("roadmap", []),
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[ROADMAPS_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        logger.info("Created roadmap", extra={"user_id": user_id, "roadmap_id": document["_id"]})
        return document
    except Exception as exc:
        logger.error("Failed to create roadmap", exc_info=exc, extra={"user_id": user_id, "skill": skill})
        return {"error": "database_error", "message": "Could not create roadmap."}
