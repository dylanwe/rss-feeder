import os
from dotenv import load_dotenv

load_dotenv()

POCKET_CONSUMER_KEY = os.getenv("POCKET_CONSUMER_KEY")
REDIRECT_URI = "http://localhost:8000/api/v2/pocket/callback"
ARTICLE_LIMIT = 10

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")


def sanitize_tag(tag: str) -> str:
    return "".join([c if c.isalnum() else "-" for c in tag])
