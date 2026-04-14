from typing import Any, Dict, List

STATIC_JOB_POSTINGS = [
    {"title": "Software Engineer", "company": "TechCorp", "required_score": 80},
    {"title": "Data Scientist", "company": "DataWorks", "required_score": 85},
    {"title": "Product Manager", "company": "Insight Labs", "required_score": 80},
    {"title": "DevOps Engineer", "company": "InfraOps", "required_score": 90},
    {"title": "AI Specialist", "company": "NeuroAI", "required_score": 95},
]


def build_job_matches(resume_score: float) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for posting in STATIC_JOB_POSTINGS:
        if resume_score < posting["required_score"]:
            continue
        percentage = min(100.0, (resume_score / posting["required_score"]) * 100)
        matches.append(
            {
                "title": posting["title"],
                "company": posting["company"],
                "match_percentage": round(percentage, 1),
            }
        )
    return matches
