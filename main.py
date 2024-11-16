from fastapi import FastAPI
import feedparser
from pydantic.dataclasses import dataclass

app = FastAPI()

@dataclass
class Article:
    url: str

@dataclass
class RssFeed:
    title: str
    articles: list[Article]

async def get_rss_feed(rss_link: str):
    parsed_feed = feedparser.parse(rss_link)
    articles = []

    for entry in parsed_feed.entries[:5]:
        articles.append(Article(url=entry.link))

    return RssFeed(title=parsed_feed.feed.title, articles=articles)

@app.get("/")
async def read_root():
    rss_links = [
        "https://xeiaso.net/blog.rss",
        "https://world.hey.com/dhh/feed.atom",
        "https://fasterthanli.me/index.xml"
    ]

    feeds = []
    for link in rss_links:
        feeds.append(await get_rss_feed(link))

    # TODO: save to Pocket

    return feeds
