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

@rss_router.get("/feeds")
async def get_rss_feeds():
    conn = sqlite3.connect("feeds.db")
    rss_links = conn.execute("SELECT title, url FROM feeds").fetchall()
    conn.close()

    feeds = []
    for row in rss_links:
        feeds.append({"title": row[0], "url": row[1]})

    return feeds

@rss_router.patch("/feeds")
async def refresh_feeds():
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



@rss_router.post("/feeds")
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

@rss_router.delete("/feeds")
async def delete_rss_feed(request: FeedPostRequest):
    try:
        print(request.rss_link)
        (tag, articles) = await get_rss_feed(request.rss_link)
        saved_articles = await get_rss_feeds_from_tag({tag})
        if saved_articles[tag] is not None and len(saved_articles[tag]) is not 0:
            item_ids = set([article.item_id for article in saved_articles[tag] if article.link in [article.link for article in articles]])
            await delete_articles({tag: item_ids})

        conn = sqlite3.connect("feeds.db")
        conn.execute("DELETE FROM feeds WHERE url = ?", (request.rss_link,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "failed"}


