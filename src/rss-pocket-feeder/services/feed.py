from dataclasses import dataclass
from repositories.feed import FeedRepository, Feed
from repositories.rss import RSSRepository
from repositories.pocket import PocketRepository
from typing import List
import logging

logger = logging.getLogger('uvicorn.error')

@dataclass
class RefreshedStatus:
    saved: dict[str, set[str]]
    deleted: dict[str, set[int]]

class FeedService:
    def __init__(
            self,
            feed_repository: FeedRepository = FeedRepository(),
            pocket_repository: PocketRepository = PocketRepository(),
            rss_repository: RSSRepository = RSSRepository()
    ):
        self.feed_repository = feed_repository
        self.pocket_repository = pocket_repository
        self.rss_repository = rss_repository

    async def get_feed(self, url: str, access_token: str) -> Feed:
        return await self.feed_repository.get_feed(url=url, access_token=access_token)

    async def get_feeds(self, access_token: str) -> List[Feed]:
        return await self.feed_repository.get_feeds(access_token)

    async def save_feed(self, rss_link: str, access_token: str):
        (title, _) = await self.rss_repository.get_rss_feed(rss_link)
        await self.feed_repository.save_feed(title=title, url=rss_link, access_token=access_token)

    async def refresh_feeds(self, access_token: str) -> RefreshedStatus:
        rss_links = await self.feed_repository.get_feeds(access_token=access_token)
        logger.info(f"Refreshing {len(rss_links)} feeds")

        feeds = {}
        for rss_link in rss_links:
            link = rss_link.url
            (tag, article_urls) = await self.rss_repository.get_rss_feed(link)
            feeds[tag] = article_urls

        saved_feeds = await self.pocket_repository.get_rss_feeds_from_tag(set(feeds.keys()), access_token)
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

        # filter out empty sets
        to_save = {tag: urls for tag, urls in to_save.items() if urls}
        to_delete = {tag: ids for tag, ids in to_delete.items() if ids}

        logger.info(f"To save: {to_save}")
        logger.info(f"To delete: {to_delete}")

        if to_save:
            await self.pocket_repository.save_articles(to_save, access_token)
        if to_delete:
            await self.pocket_repository.delete_articles(to_delete, access_token)

        return RefreshedStatus(saved=to_save, deleted=to_delete)


    async def delete_feed(self, rss_link: str, access_token: str):
        (tag, articles) = await self.rss_repository.get_rss_feed(rss_link)
        saved_articles = await self.pocket_repository.get_rss_feeds_from_tag({tag}, access_token)
        if saved_articles[tag] is not None and len(saved_articles[tag]) != 0:
            item_ids = set([article.item_id for article in saved_articles[tag] if article.link in [article.link for article in articles]])
            await self.pocket_repository.delete_articles({tag: item_ids}, access_token)

        await self.feed_repository.delete_feed(rss_link, access_token)

