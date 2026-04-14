from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

USERS_COLLECTION = "users"

BADGE_RULES = [
    ("First XP", lambda xp, streak: xp >= 1),
    ("Learner", lambda xp, streak: xp >= 100),
    ("Driven", lambda xp, streak: xp >= 500),
    ("Veteran", lambda xp, streak: xp >= 1000),
    ("Streak Starter", lambda xp, streak: streak >= 3),
    ("Consistency Champion", lambda xp, streak: streak >= 7),
    ("Daily Habit", lambda xp, streak: streak >= 14),
]


def calculate_level(xp: int) -> int:
    if xp < 0:
        return 1

    level = 1
    while xp >= xp_required_for_level(level + 1):
        level += 1
    return level


def xp_required_for_level(level: int) -> int:
    return 100 * (level - 1) * (level - 1)


def determine_badges(xp: int, streak: int, additional_badges: Optional[List[str]] = None) -> List[str]:
    earned = {badge for badge, rule in BADGE_RULES if rule(xp, streak)}
    if additional_badges:
        earned.update([badge.strip() for badge in additional_badges if badge and badge.strip()])
    return sorted(earned)


def _next_day_active(last_active: Optional[datetime], current_time: datetime) -> bool:
    if not last_active:
        return False
    return (current_time.date() - last_active.date()) == timedelta(days=1)


def _same_day_active(last_active: Optional[datetime], current_time: datetime) -> bool:
    if not last_active:
        return False
    return current_time.date() == last_active.date()


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict]:
    try:
        query_id = ObjectId(user_id)
    except Exception:
        return None
    return await db[USERS_COLLECTION].find_one({"_id": query_id})


async def update_user_gamification(
    db: AsyncIOMotorDatabase,
    user_id: str,
    xp_gain: int = 0,
    activity_date: Optional[datetime] = None,
    additional_badges: Optional[List[str]] = None,
) -> Dict[str, Any]:
    now = activity_date or datetime.utcnow()
    user = await get_user_by_id(db, user_id)
    if not user:
        return {"error": "user_not_found", "message": "User not found."}

    current_xp = int(user.get("xp", 0))
    current_streak = int(user.get("streak", 0))
    last_active = user.get("last_active")

    updated_xp = max(0, current_xp + xp_gain)
    updated_level = calculate_level(updated_xp)

    if _same_day_active(last_active, now):
        updated_streak = current_streak
    elif _next_day_active(last_active, now):
        updated_streak = current_streak + 1
    else:
        updated_streak = 1

    badges = determine_badges(updated_xp, updated_streak, additional_badges)

    update_payload = {
        "xp": updated_xp,
        "level": updated_level,
        "streak": updated_streak,
        "badges": badges,
        "last_active": now,
        "updated_at": now,
    }

    result = await db[USERS_COLLECTION].update_one(
        {"_id": user["_id"]},
        {"$set": update_payload},
    )

    if result.modified_count == 0:
        return {"error": "update_failed", "message": "No changes were applied to the user record."}

    updated_user = await get_user_by_id(db, user_id)
    if updated_user:
        updated_user["_id"] = str(updated_user["_id"])
        updated_user.pop("password", None)
    return {"user": updated_user, "xp": updated_xp, "level": updated_level, "streak": updated_streak, "badges": badges}
