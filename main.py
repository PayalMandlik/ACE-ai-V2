import os
from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.staticfiles import StaticFiles

from config import settings
from routers.auth_router import router as auth_router
from routers.assessment_router import router as assessment_router
from routers.gap_router import router as gap_router
from routers.github_router import router as github_router
from routers.job_router import router as job_router
from routers.resume_router import router as resume_router
from routers.roadmap_router import router as roadmap_router
from routers.suggestions_router import router as suggestions_router
from utils.security import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(settings.mongodb_uri)
    app.mongodb = app.mongodb_client[settings.mongodb_db]
    try:
        yield
    finally:
        app.mongodb_client.close()


app = FastAPI(title="ACE AI", version="0.1.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/assets") or request.url.path.startswith("/pages") or request.url.path in {"/", "/login", "/login.html", "/signup", "/signup.html"}:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# API routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(resume_router, prefix="/resume", tags=["resume"])
app.include_router(gap_router, tags=["gap"])
app.include_router(github_router, tags=["github"])
app.include_router(roadmap_router, tags=["roadmap"])
app.include_router(assessment_router, tags=["assessment"])
app.include_router(suggestions_router, tags=["suggestions"])
app.include_router(job_router, tags=["jobs"])


# Test AI endpoint
@app.get("/test-gemini")
async def test_gemini():
    from utils.ollama_client import call_ollama

    return await call_ollama('Return ONLY this JSON: {"status":"ok","model":"gemini"}')


# Dashboard
@app.get("/api/dashboard")
async def dashboard_stub(current_user: dict = Depends(get_current_user)):
    user = await app.mongodb["users"].find_one({"_id": ObjectId(current_user["_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    resume_doc = await app.mongodb["resumes"].find_one(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
    )
    gap_doc = await app.mongodb["gap_analysis"].find_one(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
    )
    validation_doc = await app.mongodb["validations"].find_one(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
    )
    suggestions_doc = await app.mongodb["suggestions"].find_one(
        {"user_id": current_user["_id"]},
        sort=[("created_at", -1)],
    )

    resume_score = None
    if resume_doc and isinstance(resume_doc.get("analysis"), dict):
        resume_score = float(resume_doc["analysis"].get("score", 0))

    skill_readiness = None
    if gap_doc and isinstance(gap_doc.get("missing"), list):
        skill_readiness = max(0, 100 - min(100, len(gap_doc["missing"]) * 10))

    return {
        "status": "Live",
        "profile": {
            "name": user.get("name", "Career strategist"),
            "xp": user.get("xp", 0),
            "level": user.get("level", 1),
            "streak": user.get("streak", 0),
        },
        "stats": {
            "resumeScore": resume_score,
            "skillReadiness": skill_readiness,
            "validationStatus": "Completed" if validation_doc else "Pending",
            "nextMilestone": "Review your latest suggestions",
        },
        "activity": [
            {
                "type": "resume_analysis",
                "timestamp": resume_doc.get("created_at") if resume_doc else None,
                "status": "Completed" if resume_doc else "Not started",
            },
            {
                "type": "skill_gap_analysis",
                "timestamp": gap_doc.get("created_at") if gap_doc else None,
                "status": "Completed" if gap_doc else "Not started",
            },
            {
                "type": "github_validation",
                "timestamp": validation_doc.get("created_at") if validation_doc else None,
                "status": "Completed" if validation_doc else "Not started",
            },
            {
                "type": "suggestions",
                "timestamp": suggestions_doc.get("created_at") if suggestions_doc else None,
                "status": "Completed" if suggestions_doc else "Not started",
            },
        ],
    }


# Health check
@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "database": settings.mongodb_db}


# Static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "assets")), name="assets")
app.mount("/pages", StaticFiles(directory=os.path.join(BASE_DIR, "pages")), name="pages")


# Frontend routes
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/login")
@app.get("/login.html")
async def serve_login():
    return FileResponse(os.path.join(BASE_DIR, "login.html"))


@app.get("/signup")
@app.get("/signup.html")
async def serve_signup():
    return FileResponse(os.path.join(BASE_DIR, "signup.html"))
