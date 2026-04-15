import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from utils.gemini_client import call_gemini
from schemas.resume_schema import ResumeAnalyzeResponse

router = APIRouter()


# ✅ DB Dependency
async def get_database(request: Request) -> AsyncIOMotorDatabase:
    return request.app.mongodb


# ✅ Safe parser (handles bad AI output)
def _safe_analysis(result: str) -> Dict[str, Any]:
    default = {
        "score": 50,
        "strengths": ["Resume received"],
        "weaknesses": ["Needs improvement"],
        "missing_skills": ["Add more relevant skills"],
        "keywords": [],
        "raw_output": result,
    }

    if not result or result.startswith("Error"):
        return default

    try:
        analysis = json.loads(result)
        if not isinstance(analysis, dict):
            return default

        return {
            "score": float(analysis.get("score", 50)),
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "missing_skills": analysis.get("missing_skills", []),
            "keywords": analysis.get("keywords", []),
            "raw_output": result,
        }

    except:
        return default


# ✅ MAIN API (FIXED ROUTE)
@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(
    request: Request,
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    # ✅ Validation
    if not text and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide resume text or file",
        )

    # ✅ Read file if uploaded
    if file:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is empty",
        )

    # ✅ DIRECT PROMPT (no missing function issue)
    prompt = f"""
Analyze this resume and return ONLY valid JSON in this format:

{{
  "score": number (0-100),
  "strengths": ["point1", "point2"],
  "weaknesses": ["point1", "point2"],
  "missing_skills": ["skill1", "skill2"],
  "keywords": ["keyword1", "keyword2"]
}}

Resume:
{text}
"""

    # ✅ Call Gemini
    result = await call_gemini(prompt)
    print("Gemini Raw Response:", result)

    # ✅ Parse safely
    analysis = _safe_analysis(result)

    # ✅ Save to DB (correct schema)
    now = datetime.utcnow()
    document = {
        "user_id": "demo_user",   # ✅ avoid auth issues
        "resume_text": text,
        "analysis": analysis,     # ✅ store parsed JSON (IMPORTANT FIX)
        "created_at": now,
        "updated_at": now,
    }

    try:
        await db.resumes.insert_one(document)
    except Exception as exc:
        print("MongoDB insert failed:", exc)

    # ✅ Response
    return ResumeAnalyzeResponse(
        score=analysis["score"],
        strengths=analysis["strengths"],
        weaknesses=analysis["weaknesses"],
        missing_skills=analysis["missing_skills"],
        keywords=analysis["keywords"],
        raw_output=analysis["raw_output"],
    )