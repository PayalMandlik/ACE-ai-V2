from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.assessment_agent import evaluate_assessment_answers, generate_assessment_questions

ASSESSMENTS_COLLECTION = "assessments"


async def create_assessment(
    db: AsyncIOMotorDatabase,
    skill: str,
    num_questions: int = 5,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    assessment = await generate_assessment_questions(skill, num_questions)
    if assessment.get("error"):
        return assessment

    document: Dict[str, Any] = {
        "user_id": user_id,
        "skill": skill.strip(),
        "questions": assessment.get("questions", []),
        "status": "generated",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[ASSESSMENTS_COLLECTION].insert_one(document)
    assessment_id = str(result.inserted_id)
    await db[ASSESSMENTS_COLLECTION].update_one(
        {"_id": result.inserted_id},
        {"$set": {"assessment_id": assessment_id}},
    )
    return {
        "assessment_id": assessment_id,
        "skill": document["skill"],
        "questions": document["questions"],
        "raw_output": assessment.get("raw_output"),
    }


async def submit_assessment(
    db: AsyncIOMotorDatabase,
    user_id: str,
    assessment_id: str,
    answers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    document = await db[ASSESSMENTS_COLLECTION].find_one(
        {"assessment_id": assessment_id, "user_id": user_id}
    )
    if not document:
        return {"error": "not_found", "message": "Assessment not found."}

    questions = document.get("questions", [])
    evaluation = await evaluate_assessment_answers(questions, answers)
    if evaluation.get("error"):
        return evaluation

    updated_doc: Dict[str, Any] = {
        "answers": answers,
        "score": evaluation["score"],
        "feedback": evaluation.get("feedback", []),
        "xp": evaluation.get("xp", 0),
        "status": "completed",
        "updated_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
    }
    await db[ASSESSMENTS_COLLECTION].update_one(
        {"assessment_id": assessment_id, "user_id": user_id},
        {"$set": updated_doc},
    )

    return {
        "score": evaluation["score"],
        "feedback": evaluation.get("feedback", []),
        "xp": evaluation.get("xp", 0),
        "raw_output": evaluation.get("raw_output"),
    }
