from typing import Tuple
from models import RSSItem
import feedparser
import settings

class RSSRepository:
    def __init__(self):
        pass

    async def get_rss_feed(self, rss_link: str) -> Tuple[str, list[RSSItem]]:
        parsed_feed = feedparser.parse(rss_link)
        urls = list()

        for entry in parsed_feed.entries[:settings.ARTICLE_LIMIT]:
            urls.append(RSSItem(link=entry.link))

        return (settings.sanitize_tag(parsed_feed.feed.title.lower()), urls)
