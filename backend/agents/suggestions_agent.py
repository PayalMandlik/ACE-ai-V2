import json
from typing import Any, Dict, List, Optional

from utils.gemini_client import call_gemini

_PROMPT_PREFIX = (
    "You are a career suggestion agent. Return ONLY valid JSON.\n"
    "The JSON must have exactly three keys: summary (string), suggestions (array of strings), priority_actions (array of strings).\n"
    "Example output:\n"
    '{"summary":"Key actions to advance your career.","suggestions":["Improve GitHub README","Add cloud certs"],"priority_actions":["Update resume","Practice interviews"]}\n'
    "Return ONLY valid JSON. No markdown, no explanation, no code fences.\n"
)


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


async def generate_suggestions(
    resume_text: str,
    gap_analysis: dict,
    validation: dict,
) -> Dict[str, Any]:
    prompt = (
        _PROMPT_PREFIX
        + f"Resume text:\n{resume_text or 'Not provided'}\n"
        + f"Gap analysis:\n{json.dumps(gap_analysis) if gap_analysis else 'Not provided'}\n"
        + f"Validation:\n{json.dumps(validation) if validation else 'Not provided'}\n"
    )
    payload, response = await _call_with_retry(prompt)
    if payload is None:
        return {
            "error": "parse_error",
            "message": "Unable to parse Gemini response as JSON.",
            "raw_output": response,
        }

    return {
        "summary": str(payload.get("summary", "")),
        "suggestions": [str(i) for i in _ensure_list(payload.get("suggestions", []))],
        "priority_actions": [str(i) for i in _ensure_list(payload.get("priority_actions", []))],
        "raw_output": payload,
    }