import json
from typing import Any, Dict, List, Optional

from utils.gemini_client import call_gemini

_PROMPT_PREFIX = (
    "You are a roadmap planning assistant. Given a target skill and duration, return ONLY valid JSON.\n"
    "The JSON must have exactly two keys: summary (string) and roadmap (array of objects).\n"
    "Each roadmap object must have keys: day (number) and task (string).\n"
    "Example output:\n"
    '{"summary":"A 5-day Python learning plan.","roadmap":[{"day":1,"task":"Review core syntax."},{"day":2,"task":"Build a sample project."}]}\n'
    "Return ONLY valid JSON. No markdown, no explanation, no code fences.\n"
)

_cache: Dict[str, Dict[str, Any]] = {}


def _extract_content(response: Dict[str, Any]) -> Optional[Any]:
    if not isinstance(response, dict):
        return None
    if "text" in response:
        return response["text"]
    if "choices" in response and isinstance(response["choices"], list):
        if not response["choices"]:
            return None
        return response["choices"][0].get("content")
    return response.get("output") or None


def _parse_json_text(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        ).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and first < last:
            try:
                return json.loads(cleaned[first : last + 1])
            except json.JSONDecodeError:
                return None
    return None


def _extract_json_from_response(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    content = _extract_content(response)
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        return _parse_json_text(content)
    return None


async def _call_with_retry(prompt: str) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    response = await call_gemini(prompt)
    payload = _extract_json_from_response(response)
    if payload is not None:
        return payload, response
    retry_prompt = prompt + "\nYou must return ONLY raw valid JSON. No markdown, no explanation."
    response = await call_gemini(retry_prompt)
    return _extract_json_from_response(response), response


def _ensure_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


async def generate_roadmap(skill: str, duration: str) -> Dict[str, Any]:
    cache_key = f"{skill.strip().lower()}::{duration.strip()}"
    if cache_key in _cache:
        return _cache[cache_key]

    prompt = _PROMPT_PREFIX + f"Skill: {skill.strip()}\nDuration: {duration.strip()} days\n"
    payload, response = await _call_with_retry(prompt)
    if payload is None:
        return {
            "error": "parse_error",
            "message": "Unable to parse Gemini response as JSON.",
            "raw_output": response,
        }

    roadmap_raw = payload.get("roadmap", [])
    if not isinstance(roadmap_raw, list):
        roadmap_raw = [roadmap_raw] if roadmap_raw is not None else []

    roadmap_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(roadmap_raw, start=1):
        if isinstance(item, dict):
            roadmap_items.append({"day": item.get("day", idx), "task": str(item.get("task", ""))})
        else:
            roadmap_items.append({"day": idx, "task": str(item)})

    result = {
        "summary": str(payload.get("summary", "")),
        "roadmap": roadmap_items,
        "raw_output": payload,
    }
    _cache[cache_key] = result
    return result