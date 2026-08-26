from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///smarthome.db"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "AI Smart Home"
)

DEBUG = True