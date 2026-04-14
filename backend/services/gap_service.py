import logging
from datetime import datetime
from typing import Dict, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("ace_ai")
GAP_COLLECTION = "gap_analysis"

ROLE_SKILL_MAP: Dict[str, List[str]] = {
    "software engineer": ["python", "data structures", "algorithms", "system design", "git", "unit testing"],
    "data scientist": ["python", "statistics", "machine learning", "data visualization", "sql", "feature engineering"],
    "product manager": ["roadmapping", "stakeholder management", "user research", "prioritization", "metrics", "communication"],
    "devops engineer": ["ci/cd", "cloud", "docker", "kubernetes", "infrastructure as code", "monitoring"],
}


def _normalize_skills(skills: list[str]) -> list[str]:
    return [skill.strip().lower() for skill in skills if skill and skill.strip()]


async def get_resume(db: AsyncIOMotorDatabase, resume_id: str) -> dict | None:
    try:
        return await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return None


async def analyze_gap(db: AsyncIOMotorDatabase, user_id: str, resume_id: str, target_role: str) -> dict:
    try:
        resume_doc = await get_resume(db, resume_id)
        if not resume_doc or resume_doc.get("user_id") != user_id:
            return {"error": "resume_not_found", "message": "Resume not found."}

        expected_skills = ROLE_SKILL_MAP.get(target_role.strip().lower(), [])
        resume_skills = _normalize_skills(resume_doc.get("analysis", {}).get("keywords", []))
        matched = [skill for skill in expected_skills if skill in resume_skills]
        missing = [skill for skill in expected_skills if skill not in resume_skills]
        priority = missing.copy()

        document = {
            "user_id": user_id,
            "resume_id": resume_id,
            "target_role": target_role.strip(),
            "expected_skills": expected_skills,
            "resume_skills": resume_skills,
            "matched": matched,
            "missing": missing,
            "priority": priority,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[GAP_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        logger.info("Saved gap analysis", extra={"user_id": user_id, "gap_id": document["_id"]})
        return document
    except Exception as exc:
        logger.error("Failed to analyze gap", exc_info=exc, extra={"user_id": user_id, "resume_id": resume_id})
        return {"error": "database_error", "message": "Could not save gap analysis."}
