from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.resume_agent import analyze_resume_text

RESUMES_COLLECTION = "resumes"


async def extract_resume_text(file: UploadFile, text: Optional[str] = None) -> str:
    if text and text.strip():
        return text.strip()

    raw_bytes = await file.read()
    try:
        return raw_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw_bytes.decode("latin-1").strip()


async def analyze_and_store_resume(
    db: AsyncIOMotorDatabase,
    text: Optional[str] = None,
    file: Optional[UploadFile] = None,
    user_id: str = "anonymous",
) -> Dict[str, Any]:
    resume_text = text.strip() if text else ""
    if file is not None:
        resume_text = await extract_resume_text(file, resume_text)

    if not resume_text:
        return {"error": "missing_text", "message": "Resume text is required."}

    analysis = await analyze_resume_text(resume_text)
    if analysis.get("error"):
        return analysis

    document: Dict[str, Any] = {
        "user_id": str(user_id),
        "resume_text": resume_text,
        "analysis": analysis,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[RESUMES_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
