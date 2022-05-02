import os
from dotenv import load_dotenv

load_dotenv()

MONGO_CONNECTION_STR = os.getenv("MONGO_CONNECTION_STR")
MONGO_DB_NAME = "whatdo2"
