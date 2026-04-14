import json
from typing import Any, Dict, List, Optional

from utils.ollama_client import call_ollama

# FIX: split prompts so JSON examples are concatenated, not passed through .format()
_QUESTION_PREFIX = (
    "You are an assessment generation assistant. Create ONLY valid JSON based on the request below.\n"
    "Generate one JSON object with a single key \"questions\" containing a list of objects. Each object must include keys: id, question.\n"
    "Do not include any extra keys.\n"
    "Example output:\n"
    '{"questions":[{"id":"1","question":"Explain REST APIs."},{"id":"2","question":"What is dependency injection?"}]}\n'
    "Return ONLY valid JSON. No explanation.\n"
)

_EVALUATION_PREFIX = (
    "You are an assessment evaluation assistant. Given questions and answers, return ONLY valid JSON.\n"
    "The JSON object must contain keys: score, feedback, xp. score must be a number. feedback must be an array of strings. xp must be an integer.\n"
    "Do not include any extra keys.\n"
    "Example output:\n"
    '{"score":85,"feedback":["Good reasoning","Clarify your second answer."],"xp":20}\n'
)


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


async def _call_ollama_with_retry(prompt: str) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    response = await call_ollama(prompt)
    payload = _extract_json_from_response(response)
    if payload is not None:
        return payload, response

    retry_prompt = prompt + "\nFix your JSON and return ONLY valid JSON. No explanation."
    response = await call_ollama(retry_prompt)
    return _extract_json_from_response(response), response


def _normalize_questions(questions: Any) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    if not isinstance(questions, list):
        return normalized
    for idx, question in enumerate(questions, start=1):
        if isinstance(question, dict):
            normalized.append(
                {
                    "id": str(question.get("id", idx)),
                    "question": str(question.get("question", "")).strip(),
                }
            )
        else:
            normalized.append({"id": str(idx), "question": str(question).strip()})
    return normalized


async def generate_assessment_questions(skill: str, num_questions: int = 5) -> Dict[str, Any]:
    # FIX: use concatenation to avoid KeyError on JSON braces in the example
    prompt = _QUESTION_PREFIX + f"Skill: {skill.strip()}\nNumber of questions: {num_questions}\n"
    payload, response = await _call_ollama_with_retry(prompt)
    if payload is None:
        return {"error": "parse_error", "message": "Unable to parse AI response as JSON.", "raw_output": response}

    questions = _normalize_questions(payload.get("questions", []))
    return {"questions": questions, "raw_output": payload}


async def evaluate_assessment_answers(questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    # FIX: use concatenation to avoid KeyError on JSON braces in the example
    prompt = (
        _EVALUATION_PREFIX
        + f"Questions:\n{json.dumps(questions, indent=2)}\n\nSubmitted Answers:\n{json.dumps(answers, indent=2)}\n"
        + "Return ONLY valid JSON. No explanation."
    )
    payload, response = await _call_ollama_with_retry(prompt)
    if payload is None:
        return {"error": "parse_error", "message": "Unable to parse AI response as JSON.", "raw_output": response}

    score = payload.get("score", 0)
    if not isinstance(score, (int, float)):
        try:
            score = float(score)
        except Exception:
            score = 0.0

    feedback = payload.get("feedback", [])
    if not isinstance(feedback, list):
        feedback = [str(feedback)] if feedback is not None else []

    xp = payload.get("xp", 0)
    if not isinstance(xp, int):
        try:
            xp = int(xp)
        except Exception:
            xp = 0

    return {
        "score": float(score),
        "feedback": [str(item) for item in feedback],
        "xp": xp,
        "raw_output": payload,
    }