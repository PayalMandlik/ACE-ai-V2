from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

JOBS_COLLECTION = "jobs"
RESUMES_COLLECTION = "resumes"

STATIC_JOB_POSTINGS = [
    {"title": "Software Engineer", "company": "TechCorp", "required_score": 80},
    {"title": "Data Scientist", "company": "DataWorks", "required_score": 85},
    {"title": "Product Analyst", "company": "Insight Labs", "required_score": 80},
    {"title": "DevOps Engineer", "company": "InfraOps", "required_score": 90},
    {"title": "AI Specialist", "company": "NeuroAI", "required_score": 95},
]


def _to_object_id(document_id: str) -> Optional[ObjectId]:
    try:
        return ObjectId(document_id)
    except Exception:
        return None


async def _get_resume_document(db: AsyncIOMotorDatabase, resume_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if resume_id:
        object_id = _to_object_id(resume_id)
        if object_id:
            return await db[RESUMES_COLLECTION].find_one({"_id": object_id})
        return None
    return await db[RESUMES_COLLECTION].find_one(sort=[("created_at", -1)])


def _normalize_match_percentage(score: float) -> float:
    return max(0.0, min(100.0, score))


def _build_job_matches(resume_score: float) -> List[Dict[str, Any]]:
    matches = []
    for posting in STATIC_JOB_POSTINGS:
        if resume_score < posting["required_score"]:
            continue

        match_percentage = _normalize_match_percentage((resume_score / posting["required_score"]) * 100)
        matches.append(
            {
                "title": posting["title"],
                "company": posting["company"],
                "required_score": posting["required_score"],
                "match_percentage": round(match_percentage, 1),
            }
        )
    return matches


async def match_jobs(
    db: AsyncIOMotorDatabase,
    resume_id: Optional[str] = None,
) -> Dict[str, Any]:
    resume_doc = await _get_resume_document(db, resume_id)
    if not resume_doc:
        return {"error": "resume_not_found", "message": "Resume document not found."}

    resume_score = float(resume_doc.get("analysis", {}).get("score", 0))
    if resume_score < 80:
        document = {
            "resume_id": str(resume_doc.get("_id")),
            "match_percentage": 0.0,
            "jobs": [],
            "raw_output": {"resume_score": resume_score},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db[JOBS_COLLECTION].insert_one(document)
        return document

    jobs = _build_job_matches(resume_score)
    top_match = max((job["match_percentage"] for job in jobs), default=0.0)

    document = {
        "resume_id": str(resume_doc.get("_id")),
        "match_percentage": top_match,
        "jobs": jobs,
        "raw_output": {"resume_score": resume_score},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[JOBS_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
