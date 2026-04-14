from datetime import datetime
from typing import Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

GAP_COLLECTION = "gap_analysis"

ROLE_SKILL_MAP: Dict[str, List[str]] = {
    "software engineer": [
        "python",
        "data structures",
        "algorithms",
        "system design",
        "git",
        "unit testing",
    ],
    "data scientist": [
        "python",
        "statistics",
        "machine learning",
        "data visualization",
        "sql",
        "feature engineering",
    ],
    "product manager": [
        "roadmapping",
        "stakeholder management",
        "user research",
        "prioritization",
        "metrics",
        "communication",
    ],
    "devops engineer": [
        "ci/cd",
        "cloud",
        "docker",
        "kubernetes",
        "infrastructure as code",
        "monitoring",
    ],
}


def _normalize_skills(skills: List[str]) -> List[str]:
    return [skill.strip().lower() for skill in skills if skill and skill.strip()]


async def analyze_skill_gap(
    db: AsyncIOMotorDatabase,
    target_role: str,
    resume_skills: List[str],
    user_id: Optional[str] = None,
) -> Dict[str, List[str]]:
    normalized_role = target_role.strip().lower()
    expected_skills = ROLE_SKILL_MAP.get(normalized_role, [])
    normalized_resume = _normalize_skills(resume_skills)

    matched = [skill for skill in expected_skills if skill in normalized_resume]
    missing = [skill for skill in expected_skills if skill not in normalized_resume]
    priority = missing.copy()

    document = {
        "user_id": user_id,
        "target_role": target_role.strip(),
        "expected_skills": expected_skills,
        "resume_skills": normalized_resume,
        "matched": matched,
        "missing": missing,
        "priority": priority,
        "created_at": datetime.utcnow(),
    }
    result = await db[GAP_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "priority_skills": priority,
    }