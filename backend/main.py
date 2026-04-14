import logging
import time

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.database import connect_to_mongo, close_mongo_connection, get_database
from backend.db.seed import seed_database
from backend.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from backend.routers.auth import router as auth_router
from backend.routers.assessment import router as assessment_router
from backend.routers.gap import router as gap_router
from backend.routers.github import router as github_router
from backend.routers.jobs import router as jobs_router
from backend.routers.progress import router as progress_router
from backend.routers.resume import router as resume_router
from backend.routers.roadmap import router as roadmap_router
from backend.routers.suggestions import router as suggestions_router

logger = logging.getLogger("ace_ai")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="ACE AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.rate_limit_store = {}

@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/assets") or request.url.path.startswith("/pages") or request.url.path in {"/", "/login", "/login.html", "/signup", "/signup.html"}:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(resume_router, prefix="/resume", tags=["resume"])
app.include_router(gap_router, prefix="/gap", tags=["gap"])
app.include_router(github_router, tags=["github"])
app.include_router(roadmap_router, tags=["roadmap"])
app.include_router(assessment_router, tags=["assessment"])
app.include_router(suggestions_router, tags=["suggestions"])
app.include_router(jobs_router, tags=["jobs"])
app.include_router(progress_router, prefix="/progress", tags=["progress"])

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    client_host = request.client.host if request.client else "unknown"
    now = time.time()
    window = settings.rate_limit_seconds
    bucket = app.state.rate_limit_store.get(client_host, [])
    bucket = [timestamp for timestamp in bucket if now - timestamp < window]
    bucket.append(now)
    app.state.rate_limit_store[client_host] = bucket

    if len(bucket) > settings.rate_limit_requests:
        logger.warning("Rate limit exceeded", extra={"client": client_host, "count": len(bucket)})
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limit_exceeded", "message": "Too many requests. Try again later."},
        )

    logger.info("Incoming request", extra={"method": request.method, "path": request.url.path, "client": client_host})
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        "Request completed",
        extra={"method": request.method, "path": request.url.path, "status_code": response.status_code, "duration_ms": duration_ms},
    )
    return response


@app.on_event("startup")
async def startup() -> None:
    await connect_to_mongo()
    app.mongodb = get_database()
    if app.mongodb is None:
        raise RuntimeError("MongoDB connection is not established during startup")
    try:
        await seed_database(app.mongodb)
    except Exception as exc:
        logger.error("Database seeding failed during startup", exc_info=exc)
        raise


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_mongo_connection()


@app.get("/health")
async def health() -> dict:
    status = {"status": "ok", "db": "unknown", "ollama": "unknown"}
    db = get_database()
    if db is not None:
        try:
            await db.command({"ping": 1})
            status["db"] = "ok"
        except Exception as exc:
            status["db"] = "unavailable"
            logger.error("Health check DB ping failed", exc_info=exc)
    else:
        status["db"] = "unavailable"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": "ping", "stream": False},
            )
            status["ollama"] = "ok" if response.status_code == 200 else "unavailable"
    except Exception as exc:
        status["ollama"] = "unavailable"
        logger.error("Health check Ollama ping failed", exc_info=exc)

    return status


@app.get("/debug/db-status")
async def debug_db_status() -> dict:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail={"error": "db_unavailable", "message": "Database connection is not established."})
    try:
        await db.command({"ping": 1})
        return {"status": "ok"}
    except Exception as exc:
        logger.error("DB health check failed", exc_info=exc)
        raise HTTPException(status_code=503, detail={"error": "db_unavailable", "message": "Database ping failed."})


@app.get("/debug/ollama-status")
async def debug_ollama_status() -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": "ping", "stream": False},
            )
            if response.status_code != 200:
                raise RuntimeError("Ollama returned non-200 status")
            return {"status": "ok"}
    except Exception as exc:
        logger.error("Ollama health check failed", exc_info=exc)
        raise HTTPException(status_code=503, detail={"error": "ollama_unavailable", "message": "Ollama is not reachable."})
