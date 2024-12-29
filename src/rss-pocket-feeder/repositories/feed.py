from dataclasses import dataclass
from db import get_db

@dataclass
class Feed:
    title: str
    url: str
    user_token: str

class FeedRepository:
    def __init__(self, db = next(get_db())):
        self.db = db

    async def get_feeds(self, access_token: str) -> list[Feed]:
        cur = self.db.cursor()
        cur.execute("SELECT title, url, user_token FROM feeds WHERE user_token = ?", (access_token,))
        feeds = cur.fetchall()
        feeds = [Feed(title=feed[0], url=feed[1], user_token=feed[2]) for feed in feeds]
        return feeds

    async def get_feed(self, url: str, access_token: str) -> Feed:
        cur = self.db.cursor()
        cur.execute("SELECT title, url, user_token FROM feeds WHERE url = ? AND user_token = ?", (url, access_token))
        feed = cur.fetchone()
        cur.close()
        return Feed(title=feed[0], url=feed[1], user_token=feed[2])

    async def save_feed(self, title: str, url: str, access_token: str):
        cur = self.db.cursor()
        cur.execute("INSERT INTO feeds (title, url, user_token) VALUES (?, ?, ?)", (title, url, access_token))
        self.db.commit()
        cur.close()

    async def delete_feed(self, url: str, access_token: str):
        cur = self.db.cursor()
        cur.execute("DELETE FROM feeds WHERE url = ? AND user_token = ?", (url, access_token))
        self.db.commit()
        cur.close()
