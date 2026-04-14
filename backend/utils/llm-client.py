import asyncio
import json
import os
from typing import Any, Dict

import httpx

# ---------------------------------------------------------------------------
# Gemini REST client (drop-in replacement for the Ollama client)
# Set your API key in the environment or paste it directly into GEMINI_API_KEY
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_KEY_HERE")
GEMINI_MODEL = "gemini-1.5-flash"   # fast + free tier; change to gemini-1.5-pro if needed
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)
TIMEOUT_SECONDS = 60.0
MAX_RETRIES = 2
BACKOFF_FACTOR = 1.5


def _build_payload(prompt: str) -> Dict[str, Any]:
    return {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,          # low temp → more deterministic JSON output
            "maxOutputTokens": 2048,
        },
    }


def _extract_text(data: Dict[str, Any]) -> str:
    """Pull the generated text out of Gemini's response envelope."""
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""


async def call_ollama(prompt: str) -> Dict[str, Any]:
    """
    Public interface kept as call_ollama so every agent import stays unchanged.
    Returns {"text": "<generated text>"} on success, {"error": ..., "message": ...} on failure.
    """
    payload = _build_payload(prompt)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT_SECONDS)) as client:
                response = await client.post(
                    GEMINI_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()

                text = _extract_text(data)
                if not text:
                    return {
                        "error": "empty_response",
                        "message": "Gemini returned no text content.",
                        "raw": data,
                    }

                return {"text": text, "_raw": data}

        except httpx.HTTPStatusError as exc:
            body = exc.response.text
            if attempt == MAX_RETRIES:
                return {
                    "error": "gemini_http_error",
                    "status_code": exc.response.status_code,
                    "message": body,
                    "attempts": attempt,
                }

        except httpx.RequestError as exc:
            if attempt == MAX_RETRIES:
                return {
                    "error": "gemini_request_error",
                    "message": str(exc),
                    "attempts": attempt,
                }

        except Exception as exc:
            return {
                "error": "unexpected_error",
                "message": str(exc),
            }

        await asyncio.sleep(BACKOFF_FACTOR * attempt)

    return {
        "error": "gemini_retry_exhausted",
        "message": "Exceeded maximum Gemini retry attempts.",
    }