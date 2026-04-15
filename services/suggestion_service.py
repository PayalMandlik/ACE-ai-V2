import json
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.suggestions_agent import generate_suggestions

SUGGESTIONS_COLLECTION = "suggestions"


async def _get_document_by_id(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    document_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not document_id:
        return None
    try:
        query_id = ObjectId(document_id)
    except Exception:
        return None
    return await db[collection_name].find_one({"_id": query_id})


async def _get_latest_document(
    db: AsyncIOMotorDatabase,
    collection_name: str,
) -> Optional[Dict[str, Any]]:
    return await db[collection_name].find_one(sort=[("created_at", -1)])


async def create_suggestions(
    db: AsyncIOMotorDatabase,
    resume_id: Optional[str] = None,
    gap_id: Optional[str] = None,
    validation_id: Optional[str] = None,
) -> Dict[str, Any]:
    resume_doc = await _get_document_by_id(db, "resumes", resume_id) if resume_id else await _get_latest_document(db, "resumes")
    gap_doc = await _get_document_by_id(db, "gap_analysis", gap_id) if gap_id else await _get_latest_document(db, "gap_analysis")
    validation_doc = await _get_document_by_id(db, "validations", validation_id) if validation_id else await _get_latest_document(db, "validations")

    resume_text = resume_doc.get("resume_text", "") if resume_doc else ""
    gap_analysis = gap_doc.get("missing", []) if gap_doc else []
    validation = validation_doc.get("validation", {}) if validation_doc else {}

    suggestion_payload = {
        "resume_text": resume_text,
        "gap_analysis": gap_doc or {},
        "validation": validation,
    }

    result = await generate_suggestions(resume_text, gap_doc or {}, validation)
    if result.get("error"):
        return result

    document: Dict[str, Any] = {
        "resume_id": resume_doc.get("_id") if resume_doc else None,
        "gap_id": gap_doc.get("_id") if gap_doc else None,
        "validation_id": validation_doc.get("_id") if validation_doc else None,
        "summary": result.get("summary", ""),
        "suggestions": result.get("suggestions", []),
        "priority_actions": result.get("priority_actions", []),
        "input_snapshot": suggestion_payload,
        "raw_output": result.get("raw_output"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    insert_result = await db[SUGGESTIONS_COLLECTION].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    return document
