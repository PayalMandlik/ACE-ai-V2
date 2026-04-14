import logging
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.jobs_agent import build_job_matches

logger = logging.getLogger("ace_ai")
JOBS_COLLECTION = "jobs"
RESUMES_COLLECTION = "resumes"


async def _get_resume(db: AsyncIOMotorDatabase, user_id: str, resume_id: Optional[str]) -> Optional[dict]:
    try:
        if resume_id:
            return await db[RESUMES_COLLECTION].find_one({"_id": ObjectId(resume_id), "user_id": user_id})
        return await db[RESUMES_COLLECTION].find_one({"user_id": user_id}, sort=[("created_at", -1)])
    except Exception:
        return None


async def match_jobs(db: AsyncIOMotorDatabase, user_id: str, resume_id: Optional[str]) -> Dict[str, Any]:
    try:
        resume_doc = await _get_resume(db, user_id, resume_id)
        if not resume_doc:
            return {"error": "resume_not_found", "message": "Resume not found."}

        score = float(resume_doc.get("analysis", {}).get("score", 0))
        if score < 80:
            document = {
                "user_id": user_id,
                "resume_id": str(resume_doc["_id"]),
                "match_percentage": 0.0,
                "jobs": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await db[JOBS_COLLECTION].insert_one(document)
            logger.info("Created job match with low score", extra={"user_id": user_id, "resume_id": str(resume_doc["_id"])})
            return document

        jobs = build_job_matches(score)
        match_percentage = max((job["match_percentage"] for job in jobs), default=0.0)
        document = {
            "user_id": user_id,
            "resume_id": str(resume_doc["_id"]),
            "match_percentage": match_percentage,
            "jobs": jobs,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[JOBS_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        logger.info("Created job match", extra={"user_id": user_id, "resume_id": str(resume_doc["_id"])} )
        return document
    except Exception as exc:
        logger.error("Failed to match jobs", exc_info=exc, extra={"user_id": user_id, "resume_id": resume_id})
        return {"error": "database_error", "message": "Could not find jobs for resume."}
