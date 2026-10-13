from functools import lru_cache

from google import genai

from app.config import get_settings


@lru_cache
def get_gemini_client():

    settings = get_settings()

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    return client