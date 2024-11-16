import os
from dotenv import load_dotenv

load_dotenv()

POCKET_CONSUMER_KEY = os.getenv("POCKET_CONSUMER_KEY")
POCKET_ACCESS_TOKEN = os.getenv("POCKET_ACCESS_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ARTICLE_LIMIT = 10