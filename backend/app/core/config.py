import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env in backend/ directory is always loaded
ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///smarthome.db"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "AI Smart Home"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

DEBUG = True