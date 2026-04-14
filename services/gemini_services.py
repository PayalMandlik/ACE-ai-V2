import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_response(prompt: str):
    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            return {"error": True, "message": "Empty response from Gemini"}

        return response.text.strip()

    except Exception as e:
        return {"error": True, "message": str(e)}