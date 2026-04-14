from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.resume_schema import ResumeAnalyzeResponse
from services.resume_service import analyze_and_store_resume
from utils.security import get_current_user, get_database

router = APIRouter()


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> ResumeAnalyzeResponse:
    if not text and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either text or file must be provided for resume analysis.",
        )

    document = await analyze_and_store_resume(
        db=db,
        text=text,
        file=file,
        user_id=current_user["_id"],
    )

    analysis = document.get("analysis", {})
    if analysis.get("error"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=analysis.get("message", "Resume analysis failed."),
        )

    return ResumeAnalyzeResponse(
        score=float(analysis.get("score", 0)),
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        missing_skills=analysis.get("missing_skills", []),
        keywords=analysis.get("keywords", []),
        raw_output=analysis.get("raw_output"),
    )