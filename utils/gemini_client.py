import asyncio
import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

async def call_gemini(prompt: str):
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        text = getattr(response, "text", None)
        if text is None:
            text = getattr(response, "output", None)
        if text is None:
            text = str(response)

        return {
            "text": text,
            "output": text,
            "choices": [{"content": text}],
        }
    except Exception as e:
        return {"error": "gemini_error", "message": str(e)}