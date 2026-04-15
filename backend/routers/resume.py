from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.errors import api_error
from core.security import get_current_user
from schemas.resume import ResumeAnalyzeResponse
from services.resume_service import analyze_and_save_resume

router = APIRouter()


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    source: str = Form(...),
    text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> ResumeAnalyzeResponse:
    document = await analyze_and_save_resume(db, current_user["_id"], text=text, file=file, source=source)
    if document.get("error"):
        raise api_error("resume_analysis_failed", document.get("message", "Could not analyze resume."), status.HTTP_400_BAD_REQUEST)

    return ResumeAnalyzeResponse(
        id=document["_id"],
        resume_text=document["resume_text"],
        source=document["source"],
        analysis=document["analysis"],
    )
