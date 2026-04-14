from datetime import datetime
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.roadmap_agent import generate_roadmap

ROADMAPS_COLLECTION = "roadmaps"


async def create_roadmap(
    db: AsyncIOMotorDatabase,
    skill: str,
    duration: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    validation = await generate_roadmap(skill, duration)
    if validation.get("error"):
        return validation

    document: Dict[str, Any] = {
        "user_id": user_id,
        "skill": skill.strip(),
        "duration": duration.strip(),
        "roadmap": validation.get("roadmap", []),
        "summary": validation.get("summary", ""),
        "raw_output": validation.get("raw_output"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[ROADMAPS_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
