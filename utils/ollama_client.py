from utils.gemini_client import call_gemini

# We define 'call_ollama' but it actually calls Gemini internally
async def call_ollama(prompt: str, model: str = None):
    """
    Compatibility wrapper: Redirects Ollama calls to Gemini
    to avoid refactoring existing agents.
    """
    # Simply redirect to your existing gemini function
    return await call_gemini(prompt)