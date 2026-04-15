from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os

# ✅ FIXED IMPORTS
from config import settings
from routers.auth_router import router as auth_router
from routers.resume_router import router as resume_router
from routers.gap_router import router as gap_router
from routers.github_router import router as github_router
from routers.roadmap_router import router as roadmap_router

from routers.suggestions_router import router as suggestions_router
from routers.job_router import router as job_router

app = FastAPI(title="ACE AI", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(resume_router, prefix="/resume", tags=["resume"])
app.include_router(gap_router, prefix="/gap", tags=["gap"])
app.include_router(github_router, tags=["github"])
app.include_router(roadmap_router, tags=["roadmap"])

app.include_router(suggestions_router, tags=["suggestions"])
app.include_router(job_router, tags=["jobs"])


# Test AI endpoint
@app.get("/test-gemini")
async def test_gemini():
    from utils.gemini_client import call_gemini
    result = await call_gemini('Return ONLY this JSON: {"status":"ok","model":"gemini"}')
    return result


# MongoDB connection
@app.on_event("startup")
async def startup_db_client() -> None:
    app.mongodb_client = AsyncIOMotorClient(settings.mongodb_uri)
    app.mongodb = app.mongodb_client[settings.mongodb_db]


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    app.mongodb_client.close()


def get_database() -> AsyncIOMotorClient:
    return app.mongodb


# Dashboard stub
@app.get("/api/dashboard")
async def dashboard_stub():
    return {
        "status": "Live",
        "profile": {"name": "Career strategist", "xp": 0, "level": 1, "streak": 0},
        "stats": {
            "resumeScore": None,
            "skillReadiness": None,
            "validationStatus": "Pending",
            "nextMilestone": "Upload your resume to get started",
        },
        "activity": [],
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

from datetime import datetime
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase

from agents.roadmap_agent import generate_roadmap

ROADMAPS_COLLECTION = "roadmaps"


async def create_roadmap(
    db: AsyncIOMotorDatabase,
    skill: str,
    duration: str,
) -> Dict[str, Any]:
    validation = await generate_roadmap(skill, duration)
    if validation.get("error"):
        return validation

    document: Dict[str, Any] = {
        "skill": skill.strip(),
        "duration": duration.strip(),
        "roadmap": validation.get("roadmap", []),
        "summary": validation.get("summary", ""),
        "raw_output": validation.get("raw_output"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db[ROADMAPS_COLLECTION].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document
