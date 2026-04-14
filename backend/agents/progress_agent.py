from typing import Any, Dict


def build_progress_snapshot(roadmap: dict, completed_days: int, current_day: int) -> Dict[str, Any]:
    return {
        "roadmap": roadmap,
        "completed_days": completed_days,
        "current_day": current_day,
    }
