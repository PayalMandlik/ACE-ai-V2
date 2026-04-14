from typing import Any, Dict, List

COLLECTION_VALIDATORS: Dict[str, Dict[str, Any]] = {
    "users": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "email", "password", "xp", "level", "streak", "badges", "created_at", "updated_at"],
            "properties": {
                "name": {"bsonType": "string"},
                "email": {"bsonType": "string"},
                "password": {"bsonType": "string"},
                "xp": {"bsonType": "int"},
                "level": {"bsonType": "int"},
                "streak": {"bsonType": "int"},
                "badges": {"bsonType": "array"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "resumes": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "resume_text", "analysis", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "resume_text": {"bsonType": "string"},
                "analysis": {
                    "bsonType": "object",
                    "required": ["score", "strengths", "weaknesses", "missing_skills", "keywords"],
                    "properties": {
                        "score": {"bsonType": ["double", "int"]},
                        "strengths": {"bsonType": "array"},
                        "weaknesses": {"bsonType": "array"},
                        "missing_skills": {"bsonType": "array"},
                        "keywords": {"bsonType": "array"},
                    },
                },
                "source": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "gap_analysis": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "resume_id", "target_role", "expected_skills", "resume_skills", "matched", "missing", "priority", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "resume_id": {"bsonType": "string"},
                "target_role": {"bsonType": "string"},
                "expected_skills": {"bsonType": "array"},
                "resume_skills": {"bsonType": "array"},
                "matched": {"bsonType": "array"},
                "missing": {"bsonType": "array"},
                "priority": {"bsonType": "array"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "validations": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "repo_url", "owner", "repo", "readme", "languages", "validation", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "repo_url": {"bsonType": "string"},
                "owner": {"bsonType": "string"},
                "repo": {"bsonType": "string"},
                "readme": {"bsonType": "string"},
                "languages": {"bsonType": "array"},
                "validation": {
                    "bsonType": "object",
                    "required": ["summary", "skills", "score", "weaknesses"],
                    "properties": {
                        "summary": {"bsonType": "string"},
                        "skills": {"bsonType": "array"},
                        "score": {"bsonType": ["double", "int"]},
                        "weaknesses": {"bsonType": "array"},
                    },
                },
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "roadmaps": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "skill", "duration_days", "roadmap", "status", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "skill": {"bsonType": "string"},
                "duration_days": {"bsonType": "int"},
                "roadmap": {"bsonType": "array"},
                "status": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "assessments": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "assessment_id", "skill", "questions", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "assessment_id": {"bsonType": "string"},
                "skill": {"bsonType": "string"},
                "questions": {"bsonType": "array"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "suggestions": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "summary", "suggestions", "priority_actions", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "resume_id": {"bsonType": ["string", "null"]},
                "gap_id": {"bsonType": ["string", "null"]},
                "validation_id": {"bsonType": ["string", "null"]},
                "summary": {"bsonType": "string"},
                "suggestions": {"bsonType": "array"},
                "priority_actions": {"bsonType": "array"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "jobs": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "resume_id", "match_percentage", "jobs", "created_at", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "resume_id": {"bsonType": "string"},
                "match_percentage": {"bsonType": ["double", "int"]},
                "jobs": {"bsonType": "array"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "progress": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "roadmap_id", "completed_days", "current_day", "updated_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "roadmap_id": {"bsonType": "string"},
                "skill": {"bsonType": "string"},
                "completed_days": {"bsonType": "int"},
                "current_day": {"bsonType": "int"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
            },
        }
    },
    "refresh_tokens": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "token", "created_at", "updated_at", "expires_at"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "token": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
                "updated_at": {"bsonType": "date"},
                "expires_at": {"bsonType": "date"},
            },
        }
    },
}

INDEX_DEFINITIONS: Dict[str, List[Dict[str, Any]]] = {
    "users": [{"keys": [("email", 1)], "options": {"unique": True}}],
    "resumes": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "gap_analysis": [{"keys": [("user_id", 1), ("resume_id", 1)]}],
    "validations": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "roadmaps": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "assessments": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "suggestions": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "jobs": [{"keys": [("user_id", 1), ("created_at", -1)]}],
    "progress": [{"keys": [("user_id", 1), ("roadmap_id", 1)], "options": {"unique": True}}],
    "refresh_tokens": [
        {"keys": [("token", 1)], "options": {"unique": True}},
        {"keys": [("expires_at", 1)], "options": {"expireAfterSeconds": 0}},
    ],
}
