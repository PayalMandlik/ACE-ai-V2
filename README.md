# ACE AI — Autonomous Career Execution Agent

ACE AI is a hybrid career automation project built with FastAPI, Python, and Vanilla HTML/CSS/JS. It combines modular AI agent modules, MongoDB persistence, and service-oriented routing to support resume analysis, job matching, skills gap analysis, GitHub validation, career roadmap creation, and suggestion generation.

## Overview

This repository is organized around a backend API and a lightweight frontend application. The backend uses FastAPI and Motor to connect to MongoDB. The frontend is implemented with vanilla HTML, CSS, and JavaScript.

The core functionality includes:
- Resume analysis and job recommendations
- Skill gap diagnosis and career roadmap generation
- GitHub repository validation for portfolio review
- AI-driven suggestions for career improvement
- Auth-enabled token-based access for protected endpoints

## Architecture

The system separates concerns into three main layers:
1. Frontend: static pages, assets, and browser interaction
2. Backend: FastAPI routers, services, schemas, and middleware
3. AI agent modules: resume, roadmap, suggestions, assessment, and GitHub validation

The repository also contains a `backend/` package with an extended FastAPI service implementation that supports additional debug and health endpoints.

## File Structure

```text
ACE-ai-V2/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── index.html
├── login.html
├── signup.html
├── pages/
│   ├── assessment.html
│   ├── dashboard.html
│   ├── resume-analyzer.html
│   ├── roadmap.html
│   ├── skill-gap.html
│   ├── suggestions.html
│   └── validation.html
├── assets/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       ├── app.js
│       ├── assessment.js
│       ├── auth.js
│       ├── dashboard.js
│       ├── resumeAnalyzer.js
│       ├── roadmap.js
│       ├── skillGap.js
│       ├── suggestions.js
│       └── validation.js
├── agents/
│   ├── assessment_agent.py
│   ├── github_validator.py
│   ├── resume_agent.py
│   ├── roadmap_agent.py
│   ├── suggestions_agent.py
│   └── __init__.py
├── routers/
│   ├── auth_router.py
│   ├── assessment_router.py
│   ├── gap_router.py
│   ├── github_router.py
│   ├── job_router.py
│   ├── roadmap_router.py
│   ├── resume_router.py
│   ├── suggestions_router.py
│   └── __init__.py
├── services/
│   ├── auth_service.py
│   ├── assessment_service.py
│   ├── gap_service.py
│   ├── github_validation_service.py
│   ├── job_service.py
│   ├── roadmap_service.py
│   ├── resume_service.py
│   ├── suggestion_service.py
│   ├── gamification_service.py
│   └── github_validation_service.py
├── schemas/
│   ├── auth_schema.py
│   ├── assessment_schema.py
│   ├── gap_schema.py
│   ├── github_schema.py
│   ├── job_schema.py
│   ├── roadmap_schema.py
│   ├── resume_schema.py
│   └── suggestions_schema.py
├── utils/
│   ├── gemini_client.py
│   ├── ollama_client.py
│   └── security.py
├── backend/
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
└── update_db.py
```

## Setup Instructions

### 1. Create a Python environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root or export environment variables:

```env
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DB="ace_ai"
SECRET_KEY="replace-with-a-secure-key"
DEBUG=true
GEMINI_API_KEY="your-gemini-key"
```

### 4. Run the backend service

Use one of the available entrypoints:

```bash
uvicorn backend.main:app --reload --port 8000
```

If you need the lightweight static server, use:

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open the frontend

Open `index.html` in the browser or serve pages from the backend service.

### 6. Handle CORS if needed

The backend default allows all origins (`CORS_ORIGINS=["*"]`). For production, set a restricted origin list in `.env`.

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user and return access token |
| POST | `/auth/login` | Authenticate and return access token |

### Resume Analysis

| Method | Endpoint | Description |
|---|---|---|
| POST | `/resume/analyze` | Analyze resume text or uploaded file and store analysis |

### Skill Gap Analysis

| Method | Endpoint | Description |
|---|---|---|
| POST | `/gap/analyze` | Compare resume skills against a target role |

### GitHub Validation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/validate/github` | Validate a GitHub repo for portfolio readiness |

### Job Matching

| Method | Endpoint | Description |
|---|---|---|
| GET | `/jobs` | Retrieve job matches, optionally by `resume_id` |

### Roadmap Generation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/roadmap` | Generate a skill roadmap for a target skill and duration |

### Suggestions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/suggestions` | Generate career suggestions via query parameters |

### Assessment

| Method | Endpoint | Description |
|---|---|---|
| GET | `/assessment` | Create an assessment for a skill |
| POST | `/assessment/submit` | Submit assessment answers and receive feedback |

### Progress

| Method | Endpoint | Description |
|---|---|---|
| GET | `/progress/{roadmap_id}` | Get progress for a roadmap |
| POST | `/progress/update` | Update roadmap progress |

### Health & Debug

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/debug/db-status` | MongoDB health status |
| GET | `/debug/ollama-status` | Ollama health status |

## System Analysis

### Strengths

- Modular routing and service layers keep business logic separate from API layer.
- Agent-style modules are grouped by concern: resume, GitHub validation, roadmap, assessment, suggestions.
- MongoDB persistence is supported and can store resumes, assessments, roadmaps, and suggestions.
- The backend includes middleware for logging, error handling, and rate limiting in `backend/main.py`.

### Weaknesses

- The frontend uses vanilla HTML/CSS/JS and does not leverage a modern SPA framework.
- Many AI modules depend on language model clients and synthetic text responses rather than fully validated production pipelines.
- The top-level project contains both root and `backend/` entrypoints, which may cause confusion during deployment.

### Vulnerabilities

- Default CORS configuration is wide open (`["*"]`), which is suitable for development but not production.
- Authentication is not enforced on all routes, so public API surfaces may expose sensitive logic.
- Input validation is handled in some routers but may not be consistent across every endpoint.
- Secret keys and API keys must be stored securely in `.env`; default values are insecure.

## Notes

- The project currently uses a hybrid of root and backend structures; the `backend/` package contains the more complete FastAPI service.
- If you extend the project with a custom reinforcement learning environment, document the new environment and reward flow in a separate module.
- MongoDB is optional for development, but the full feature set requires an active MongoDB instance.
