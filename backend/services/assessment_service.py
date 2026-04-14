import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.assessment_agent import evaluate_answers, generate_assessment_questions

logger = logging.getLogger("ace_ai")
ASSESSMENTS_COLLECTION = "assessments"


async def generate_assessment(db: AsyncIOMotorDatabase, user_id: str, skill: str, roadmap_id: str | None = None) -> Dict[str, Any]:
    try:
        assessment_data = await generate_assessment_questions(skill)
        if assessment_data.get("error"):
            return assessment_data

        document = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "skill": skill.strip(),
            "questions": assessment_data.get("questions", []),
            "answers": [],
            "score": 0,
            "feedback": [],
            "xp": 0,
            "status": "generated",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db[ASSESSMENTS_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
        document["assessment_id"] = str(result.inserted_id)
        logger.info("Generated assessment", extra={"user_id": user_id, "assessment_id": document["assessment_id"]})
        return document
    except Exception as exc:
        logger.error("Failed to generate assessment", exc_info=exc, extra={"user_id": user_id, "skill": skill})
        return {"error": "database_error", "message": "Could not generate assessment."}


async def submit_assessment(db: AsyncIOMotorDatabase, user_id: str, assessment_id: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    try:
        object_id = ObjectId(assessment_id)
    except Exception:
        return {"error": "invalid_assessment_id", "message": "Invalid assessment id."}

    try:
        assessment = await db[ASSESSMENTS_COLLECTION].find_one({"_id": object_id, "user_id": user_id})
        if not assessment:
            return {"error": "assessment_not_found", "message": "Assessment not found."}

        evaluation = await evaluate_answers(assessment.get("questions", []), answers)
        if evaluation.get("error"):
            return evaluation

        update = {
            "answers": answers,
            "score": evaluation.get("score", 0),
            "feedback": evaluation.get("feedback", []),
            "xp": evaluation.get("xp", 0),
            "status": "completed",
            "updated_at": datetime.utcnow(),
        }
        await db[ASSESSMENTS_COLLECTION].update_one({"_id": object_id}, {"$set": update})
        logger.info("Submitted assessment", extra={"user_id": user_id, "assessment_id": assessment_id})
        return {"score": update["score"], "feedback": update["feedback"], "xp": update["xp"]}
    except Exception as exc:
        logger.error("Failed to submit assessment", exc_info=exc, extra={"user_id": user_id, "assessment_id": assessment_id})
        return {"error": "database_error", "message": "Could not submit assessment."}
