import datetime
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("ace_ai.seed")


def _collection_docs(collection_name: str) -> list[dict]:
    now = datetime.datetime.utcnow()
    if collection_name == "users":
        return [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "password": "securepassword123",
                "created_at": now,
            },
            {
                "name": "Bob Lee",
                "email": "bob@example.com",
                "password": "strongpass456",
                "created_at": now,
            },
        ]

    if collection_name == "resumes":
        return [
            {
                "user_id": "alice@example.com",
                "skills": ["Python", "FastAPI", "MongoDB"],
                "experience": "3 years building backend APIs and data-oriented services.",
                "projects": [
                    "Career assistant API", "Resume parser", "Skill gap analyzer"
                ],
                "analysis": {
                    "strengths": ["API development", "database design"],
                    "weaknesses": ["cloud deployment", "system architecture"],
                    "score": 82,
                },
                "created_at": now,
            },
            {
                "user_id": "bob@example.com",
                "skills": ["JavaScript", "React", "Node.js"],
                "experience": "4 years in full stack product delivery.",
                "projects": ["Job matching portal", "Skill tracker"],
                "analysis": {
                    "strengths": ["frontend UI", "user workflows"],
                    "weaknesses": ["machine learning", "backend optimization"],
                    "score": 76,
                },
                "created_at": now,
            },
        ]

    if collection_name == "skill_gaps":
        return [
            {
                "user_id": "alice@example.com",
                "missing_skills": ["Docker", "Kubernetes", "AWS"],
                "target_role": "Backend Engineer",
                "created_at": now,
            },
            {
                "user_id": "bob@example.com",
                "missing_skills": ["Python", "Django", "data modeling"],
                "target_role": "Technical Product Manager",
                "created_at": now,
            },
        ]

    if collection_name == "roadmaps":
        return [
            {
                "user_id": "alice@example.com",
                "steps": [
                    {"day": 1, "topic": "MongoDB fundamentals", "resource": "https://www.mongodb.com/docs/manual/"},
                    {"day": 2, "topic": "Async Python with FastAPI", "resource": "https://fastapi.tiangolo.com/"},
                    {"day": 3, "topic": "Deploying backend services", "resource": "https://docs.docker.com/"},
                ],
                "created_at": now,
            },
            {
                "user_id": "bob@example.com",
                "steps": [
                    {"day": 1, "topic": "Product roadmap planning", "resource": "https://www.aha.io/roadmapping/guide"},
                    {"day": 2, "topic": "Stakeholder communication", "resource": "https://www.atlassian.com/team-playbook/plays/"},
                ],
                "created_at": now,
            },
        ]

    if collection_name == "assessments":
        return [
            {
                "user_id": "alice@example.com",
                "skill": "Python",
                "questions": [
                    {"question": "What is a coroutine?", "answer": "A function that can pause and resume execution."},
                    {"question": "How do you create an async endpoint in FastAPI?", "answer": "Define the path operation with async def."},
                ],
                "score": 88,
                "created_at": now,
            },
            {
                "user_id": "bob@example.com",
                "skill": "Product Management",
                "questions": [
                    {"question": "What is a product strategy?", "answer": "A plan to achieve business goals through product decisions."},
                    {"question": "How do you prioritize features?", "answer": "Use impact, effort, and customer value."},
                ],
                "score": 81,
                "created_at": now,
            },
        ]

    if collection_name == "jobs":
        return [
            {
                "title": "Backend Engineer",
                "company": "Ace Tech",
                "skills_required": ["Python", "FastAPI", "MongoDB"],
                "match_score": 95,
                "created_at": now,
            },
            {
                "title": "Data Engineer",
                "company": "Career Labs",
                "skills_required": ["SQL", "ETL", "Python"],
                "match_score": 85,
                "created_at": now,
            },
        ]

    return []


async def _seed_collection(db: AsyncIOMotorDatabase, collection_name: str) -> None:
    collection = db[collection_name]
    try:
        count = await collection.estimated_document_count()
        if count != 0:
            logger.info("Skipping seed for existing collection", extra={"collection": collection_name, "count": count})
            return

        docs = _collection_docs(collection_name)
        if not docs:
            logger.warning("No documents defined for collection", extra={"collection": collection_name})
            return

        await collection.insert_many(docs)
        logger.info("Seeded collection", extra={"collection": collection_name, "inserted": len(docs)})
    except Exception as exc:
        logger.error("Failed to seed collection", exc_info=exc, extra={"collection": collection_name})
        raise


async def seed_database(db: AsyncIOMotorDatabase) -> None:
    if db is None:
        raise ValueError("Database connection is not available for seeding.")

    logger.info("Starting database seed")
    collection_names = ["users", "resumes", "skill_gaps", "roadmaps", "assessments", "jobs"]
    for name in collection_names:
        await _seed_collection(db, name)
    logger.info("Database seeding completed")
