import os

from dotenv import load_dotenv

load_dotenv()

MONGO_CONNECTION_STR = os.getenv("MONGO_CONNECTION_STR")
MONGO_DB_NAME = "whatdo2"

POSTGRES_HOST = "localhost"
POSTGRES_USER = os.getenv("POSTGRES_USER", "whatdo2")
POSTGRES_DB = os.getenv("POSTGRES_DB", "whatdo2")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "abc123")

POSTGRES_URI = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
    f":5432/{POSTGRES_DB}"
)
