from fastapi import APIRouter
from typing import Tuple
from pocket import get_rss_feeds_from_tag, save_articles, delete_articles
from models import RSSItem, FeedPostRequest
import sqlite3
import feedparser
import settings


rss_router = APIRouter(prefix="/rss", tags=["RSS"])

async def get_rss_feed(rss_link: str) -> Tuple[str, list[RSSItem]]:
    parsed_feed = feedparser.parse(rss_link)
    urls = list()

    for entry in parsed_feed.entries[:settings.ARTICLE_LIMIT]:
        urls.append(RSSItem(link=entry.link))

    return (settings.sanitize_tag(parsed_feed.feed.title.lower()), urls)

@rss_router.get("/feed")
async def refresh_feed():
    conn = sqlite3.connect("feeds.db")
    rss_links = conn.execute("SELECT url FROM feeds").fetchall()
    conn.close()

    feeds = {}
    for row in rss_links:
        link = row[0]
        (tag, article_urls) = await get_rss_feed(link)
        feeds[tag] = article_urls

    saved_feeds = await get_rss_feeds_from_tag(set(feeds.keys()))
    to_save: dict[str, set[str]] = {}
    to_delete: dict[str, set[int]] = {}

    for key in feeds.keys():
        urls = set([item.link for item in feeds[key]])
        saved_urls = set([item.link for item in saved_feeds[key]])
        to_save_urls = urls - saved_urls
        to_delete_urls = saved_urls - urls
        to_delete_item_ids = set([item.item_id for item in saved_feeds[key] if item.link in to_delete_urls])
        to_save[key] = to_save_urls
        to_delete[key] = to_delete_item_ids

    await save_articles(to_save)
    await delete_articles(to_delete)

    return {
        "saved": to_save,
        "deleted": to_delete
    }



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


