from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.resume_schema import ResumeAnalyzeResponse
from services.resume_service import analyze_and_store_resume
from utils.security import get_database

router = APIRouter()


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ResumeAnalyzeResponse:
    """
    Resume Analyzer (Gemini Powered)
    Supports:
    - Text input
    - File upload
    """

    # ✅ VALIDATION
    if not text and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either text or file must be provided.",
        )

    # ✅ TEMP USER (since auth removed)
    user_id = "demo_user"

    # ✅ PROCESS + STORE
    document = await analyze_and_store_resume(
        db=db,
        text=text,
        file=file,
        user_id=user_id,
    )

    # ❌ HANDLE ERROR FROM LLM
    analysis = document.get("analysis", {})
    if analysis.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=analysis.get("message", "Resume analysis failed."),
        )

    # ✅ RESPONSE
    return ResumeAnalyzeResponse(
        score=float(analysis.get("score", 0)),
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        missing_skills=analysis.get("missing_skills", []),
        keywords=analysis.get("keywords", []),
        raw_output=analysis.get("raw_output"),
    )