import logging
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.suggestions_agent import generate_suggestions

logger = logging.getLogger("ace_ai")
SUGGESTIONS_COLLECTION = "suggestions"


async def _get_document(db: AsyncIOMotorDatabase, collection_name: str, document_id: Optional[str]) -> dict | None:
    if not document_id:
        return None
    try:
        return await db[collection_name].find_one({"_id": ObjectId(document_id)})
    except Exception:
        return None


async def create_suggestions(
    db: AsyncIOMotorDatabase,
    user_id: str,
    resume_id: str | None,
    gap_id: str | None,
    validation_id: str | None,
) -> Dict[str, Any]:
    try:
        resume_doc = await _get_document(db, "resumes", resume_id) if resume_id else await db["resumes"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
        gap_doc = await _get_document(db, "gap_analysis", gap_id) if gap_id else await db["gap_analysis"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
        validation_doc = await _get_document(db, "validations", validation_id) if validation_id else await db["validations"].find_one({"user_id": user_id}, sort=[("created_at", -1)])

        if resume_doc and resume_doc.get("user_id") != user_id:
            resume_doc = None
        if gap_doc and gap_doc.get("user_id") != user_id:
            gap_doc = None
        if validation_doc and validation_doc.get("user_id") != user_id:
            validation_doc = None

        resume_text = resume_doc.get("resume_text", "") if resume_doc else ""
        gap_analysis = gap_doc or {}
        validation = validation_doc.get("validation", {}) if validation_doc else {}

        result = await generate_suggestions(resume_text, gap_analysis, validation)
        if result.get("error"):
            return result

        document = {
            "user_id": user_id,
            "resume_id": str(resume_doc["_id"]) if resume_doc else None,
            "gap_id": str(gap_doc["_id"]) if gap_doc else None,
            "validation_id": str(validation_doc["_id"]) if validation_doc else None,
            "summary": result.get("summary", ""),
            "suggestions": result.get("suggestions", []),
            "priority_actions": result.get("priority_actions", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        insert_result = await db[SUGGESTIONS_COLLECTION].insert_one(document)
        document["_id"] = str(insert_result.inserted_id)
        logger.info("Created suggestions", extra={"user_id": user_id, "suggestions_id": document["_id"]})
        return document
    except Exception as exc:
        logger.error("Failed to create suggestions", exc_info=exc, extra={"user_id": user_id})
        return {"error": "database_error", "message": "Could not generate suggestions."}
