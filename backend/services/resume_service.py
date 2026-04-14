from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.resume_agent import analyze_resume_text

RESUMES_COLLECTION = "resumes"


async def analyze_and_store_resume(
    db: AsyncIOMotorDatabase,
    text: Optional[str] = None,
    file: Optional[UploadFile] = None,
) -> Dict[str, Any]:
    resume_text = text.strip() if text else ""

    if file is not None and not resume_text:
        try:
            raw_bytes = await file.read()
            try:
                resume_text = raw_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                resume_text = raw_bytes.decode("latin-1").strip()
        except Exception as exc:
            return {"error": "file_read_error", "message": str(exc)}

    if not resume_text:
        return {"error": "empty_input", "message": "No readable resume content provided."}

    analysis = await analyze_resume_text(resume_text)
    if analysis.get("error"):
        return analysis

    document: Dict[str, Any] = {"analysis": analysis}

    # FIX: MongoDB insert is optional — app works without it
    try:
        doc = {
            "resume_text": resume_text[:1000],
            "analysis": analysis,
            "created_at": datetime.utcnow(),
        }
        result = await db[RESUMES_COLLECTION].insert_one(doc)
        document["_id"] = str(result.inserted_id)
    except Exception:
        pass

    return document