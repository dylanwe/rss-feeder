from fastapi import APIRouter
from typing import Tuple
from pocket import get_rss_feeds_from_tag, save_articles
from pydantic.dataclasses import dataclass
import sqlite3
import feedparser
import settings


rss_router = APIRouter(prefix="/rss", tags=["RSS"])

async def get_rss_feed(rss_link: str) -> Tuple[str, set[str]]:
    parsed_feed = feedparser.parse(rss_link)
    urls = set()

    for entry in parsed_feed.entries[:settings.ARTICLE_LIMIT]:
        urls.add(entry.link)

    return (parsed_feed.feed.title.lower(), urls)

@rss_router.get("/feed")
async def refresh_feed():
    conn = sqlite3.connect("feeds.db")
    rss_links = conn.execute("SELECT url FROM feeds").fetchall()
    conn.close()

    feeds = {}
    for row in rss_links:
        (title, article_urls) = await get_rss_feed(row[0])
        feeds[title] = article_urls

    saved = 0
    deleted = 0

    saved_feeds = await get_rss_feeds_from_tag(set(feeds.keys()))
    for key in feeds.keys():
        to_save = feeds[key] - saved_feeds[key]
        saved += len(to_save)

        await save_articles(to_save, key)

    return {"message": f"Saved {saved} articles, deleted {deleted} articles"}


@dataclass
class FeedPostRequest:
    rss_link: str

@rss_router.post("/save")
async def save_rss_feed(request: FeedPostRequest):
    try:
        conn = sqlite3.connect("feeds.db")
        (title, _) = await get_rss_feed(request.rss_link)
        conn.execute("INSERT INTO feeds (title, url) VALUES (?, ?)", (title, request.rss_link))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "failed"}


