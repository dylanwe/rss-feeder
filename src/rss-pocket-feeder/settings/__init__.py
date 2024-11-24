import os
from dotenv import load_dotenv

load_dotenv()

POCKET_CONSUMER_KEY = os.getenv("POCKET_CONSUMER_KEY")
POCKET_ACCESS_TOKEN = os.getenv("POCKET_ACCESS_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ARTICLE_LIMIT = 10

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")


def sanitize_tag(tag: str) -> str:
    return "".join([c if c.isalnum() else "-" for c in tag])
