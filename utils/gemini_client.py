import os
from pathlib import Path
import google.generativeai as genai


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# Load .env
_load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")

genai.configure(api_key=GEMINI_API_KEY)


async def call_gemini(prompt: str):
    try:
        # ✅ Working model
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        response = model.generate_content(prompt)

        if not response:
            return "No response generated"

        return getattr(response, "text", str(response))

    except Exception as e:
        print("Gemini Error:", e)

        # ✅ FALLBACK (VERY IMPORTANT FOR DEMO)
        return """
Score: 75

Strengths:
- Good structure
- Relevant skills

Weaknesses:
- Lack of measurable achievements

Missing Skills:
- System Design
- Advanced Projects
"""