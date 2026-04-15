from datetime import datetime
from typing import Dict, List

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
) -> Dict[str, List[str]]:

    normalized_role = target_role.strip().lower()
    normalized_resume = _normalize_skills(resume_skills)

    # ✅ SMART ROLE MATCHING (FIXED)
    expected_skills = []
    for role_key in ROLE_SKILL_MAP:
        if role_key in normalized_role:
            expected_skills = ROLE_SKILL_MAP[role_key]
            break

    # ✅ FALLBACK (IMPORTANT FOR DEMO)
    if not expected_skills:
        expected_skills = ["python", "communication", "problem solving"]

    # ✅ CALCULATIONS
    matched = [skill for skill in expected_skills if skill in normalized_resume]
    missing = [skill for skill in expected_skills if skill not in normalized_resume]
    priority = missing.copy()

    # ✅ DEBUG (you can remove later)
    print("ROLE:", normalized_role)
    print("EXPECTED:", expected_skills)
    print("RESUME:", normalized_resume)
    print("MATCHED:", matched)
    print("MISSING:", missing)

    # ✅ SAVE TO DB (FIXED SCHEMA)
    document = {
        "user_id": "demo_user",
        "resume_id": "demo_resume_id",
        "target_role": target_role,
        "expected_skills": expected_skills,
        "resume_skills": resume_skills,
        "matched": matched,
        "missing": missing,
        "priority": priority,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        result = await db[GAP_COLLECTION].insert_one(document)
        document["_id"] = str(result.inserted_id)
    except Exception as e:
        print("MongoDB Error:", e)

    # ✅ RETURN RESPONSE
    return {
        "matched": matched,
        "missing": missing,
        "priority": priority,
    }