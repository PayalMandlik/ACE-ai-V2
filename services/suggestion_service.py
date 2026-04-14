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
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if not document_id:
        return None
    try:
        query_id = ObjectId(document_id)
    except Exception:
        return None
    query = {"_id": query_id}
    if user_id:
        query["user_id"] = user_id
    return await db[collection_name].find_one(query)


async def _get_latest_document(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    query = {"user_id": user_id} if user_id else {}
    return await db[collection_name].find_one(query, sort=[("created_at", -1)])


async def create_suggestions(
    db: AsyncIOMotorDatabase,
    resume_id: Optional[str] = None,
    gap_id: Optional[str] = None,
    validation_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    resume_doc = (
        await _get_document_by_id(db, "resumes", resume_id, user_id)
        if resume_id
        else await _get_latest_document(db, "resumes", user_id)
    )
    gap_doc = (
        await _get_document_by_id(db, "gap_analysis", gap_id, user_id)
        if gap_id
        else await _get_latest_document(db, "gap_analysis", user_id)
    )
    validation_doc = (
        await _get_document_by_id(db, "validations", validation_id, user_id)
        if validation_id
        else await _get_latest_document(db, "validations", user_id)
    )

    if not resume_doc and not gap_doc and not validation_doc:
        return {
            "error": "no_context",
            "message": "No resume, gap analysis, or validation data available for suggestions.",
        }

    resume_text = resume_doc.get("resume_text", "") if resume_doc else ""
    gap_analysis = {
        "target_role": gap_doc.get("target_role"),
        "expected_skills": gap_doc.get("expected_skills", []),
        "resume_skills": gap_doc.get("resume_skills", []),
        "matched": gap_doc.get("matched", []),
        "missing": gap_doc.get("missing", []),
        "priority": gap_doc.get("priority", []),
    } if gap_doc else {}
    validation = validation_doc.get("validation", {}) if validation_doc else {}

    result = await generate_suggestions(resume_text, gap_analysis, validation)
    if result.get("error"):
        return result

    document: Dict[str, Any] = {
        "user_id": user_id,
        "resume_id": str(resume_doc.get("_id")) if resume_doc and resume_doc.get("_id") is not None else None,
        "gap_id": str(gap_doc.get("_id")) if gap_doc and gap_doc.get("_id") is not None else None,
        "validation_id": str(validation_doc.get("_id")) if validation_doc and validation_doc.get("_id") is not None else None,
        "summary": result.get("summary", ""),
        "focus": result.get("focus", []),
        "advice": result.get("advice", []),
        "avoid": result.get("avoid", []),
        "input_snapshot": {
            "resume_text": resume_text,
            "gap_analysis": gap_analysis,
            "validation": validation,
        },
        "raw_output": result.get("raw_output"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    insert_result = await db[SUGGESTIONS_COLLECTION].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    return document
