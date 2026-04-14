from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.database import get_database
from backend.core.errors import api_error

from schemas.resume import ResumeAnalyzeResponse
from services.resume_service import analyze_and_save_resume

router = APIRouter(prefix="/resume")


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    source: str = Form(...),  # "text" | "file"
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ResumeAnalyzeResponse:
    """
    Resume Analyzer V2 (Gemini Powered)
    """

    # 🧠 1. VALIDATE INPUT
    if source == "text" and not text:
        raise api_error(
            "invalid_input",
            "Text is required when source is 'text'",
            status.HTTP_400_BAD_REQUEST,
        )

    if source == "file" and not file:
        raise api_error(
            "invalid_input",
            "File is required when source is 'file'",
            status.HTTP_400_BAD_REQUEST,
        )

    if source not in ["text", "file"]:
        raise api_error(
            "invalid_source",
            "Source must be 'text' or 'file'",
            status.HTTP_400_BAD_REQUEST,
        )

    # 🧠 2. TEMP USER (since auth removed)
    user_id = "demo_user"

    # 🧠 3. PROCESS + SAVE (Gemini inside service)
    document = await analyze_and_save_resume(
        db=db,
        user_id=user_id,
        text=text,
        file=file,
        source=source,
    )

    # ❌ HANDLE FAILURE
    if document.get("error"):
        raise api_error(
            "resume_analysis_failed",
            document.get("message", "Could not analyze resume."),
            status.HTTP_400_BAD_REQUEST,
        )

    # ✅ SUCCESS RESPONSE
    return ResumeAnalyzeResponse(
        id=str(document["_id"]),
        resume_text=document["resume_text"],
        source=document["source"],
        analysis=document["analysis"],
    )