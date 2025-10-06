import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_URL = os.getenv(
        "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
    )
    MODEL = os.getenv("MODEL", "openai/gpt-4o")
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "openai/gpt-4o")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.0))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")