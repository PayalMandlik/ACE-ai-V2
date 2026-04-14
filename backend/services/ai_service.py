import os
import json
from google.generativeai import GenerativeModel
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = GenerativeModel("gemini-1.5-flash")


def call_gemini(prompt: str) -> dict:
    """
    Central Gemini call with strict JSON parsing
    """
    try:
        response = model.generate_content(prompt)

        text = response.text.strip()

        # Try parsing JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # محاولة تنظيف الرد
            cleaned = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)

    except Exception as e:
        print("Gemini Error:", str(e))
        return {
            "error": "AI processing failed",
            "details": str(e)
        }