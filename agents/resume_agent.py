import json
from typing import Any, Dict, List, Optional

from utils.gemini_client import call_gemini

# FIX: split prompt so the JSON example is concatenated, not passed through .format()
# Previously the example JSON like {"score":88.5} caused KeyError in .format()
_PROMPT_PREFIX = (
    "You are a resume intelligence assistant. Analyze the resume text and return ONLY valid JSON with keys: score, strengths, weaknesses, missing_skills, keywords.\n"
    "score must be a number. strengths, weaknesses, missing_skills, and keywords must be arrays.\n"
    "Example output:\n"
    '{"score":88.5,"strengths":["problem solving"],"weaknesses":["time management"],"missing_skills":["cloud computing"],"keywords":["python","api"]}\n'
    "Return ONLY valid JSON. No explanation.\n"
    "Resume text:\n"
)

_cache: Dict[str, Dict[str, Any]] = {}


def _extract_content(response: Dict[str, Any]) -> Optional[Any]:
    if not isinstance(response, dict):
        return None
    if "choices" in response and isinstance(response["choices"], list):
        if not response["choices"]:
            return None
        return response["choices"][0].get("content")
    return response.get("text") or response.get("output") or None


def _parse_json_text(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and first < last:
            try:
                return json.loads(cleaned[first:last + 1])
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


async def _call_gemini_with_retry(prompt: str) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    response = await call_gemini(prompt)
    payload = _extract_json_from_response(response)
    if payload is not None:
        return payload, response

    retry_prompt = prompt + "\nFix your JSON and return ONLY valid JSON. No explanation."
    response = await call_gemini(retry_prompt)
    return _extract_json_from_response(response), response


def _ensure_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


async def analyze_resume_text(resume_text: str) -> Dict[str, Any]:
    cache_key = resume_text.strip()
    if cache_key in _cache:
        return _cache[cache_key]

    # FIX: use concatenation instead of .format() to avoid KeyError on JSON braces
    prompt = _PROMPT_PREFIX + resume_text.strip() + "\n"
    payload, response = await _call_gemini_with_retry(prompt)
    if payload is None:
        return {"error": "parse_error", "message": "Unable to parse Gemini response as JSON.", "raw_output": response}

    score = payload.get("score", 0)
    if not isinstance(score, (int, float)):
        try:
            score = float(score)
        except Exception:
            score = 0.0

    result = {
        "score": float(score),
        "strengths": [str(item) for item in _ensure_list(payload.get("strengths", []))],
        "weaknesses": [str(item) for item in _ensure_list(payload.get("weaknesses", []))],
        "missing_skills": [str(item) for item in _ensure_list(payload.get("missing_skills", []))],
        "keywords": [str(item) for item in _ensure_list(payload.get("keywords", []))],
        "raw_output": payload,
    }
    _cache[cache_key] = result
    return result