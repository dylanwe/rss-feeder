from fastapi import HTTPException
from typing import Tuple

from models import PocketItem
import asyncio
import requests
import settings
import json
import urllib.parse
import logging

logger = logging.getLogger('uvicorn.error')
POCKET_BASE_URL = "https://getpocket.com"

class PocketRepository:
    def __init__(self):
        pass

    async def get_rss_feed(self, tag: str, access_token: str) -> Tuple[str, list[PocketItem]]:
        url = f"{POCKET_BASE_URL}/v3/get"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "consumer_key": settings.POCKET_CONSUMER_KEY,
            "access_token": access_token,
            "tag": tag,
            "count": settings.ARTICLE_LIMIT,
            "detailType": "simple"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Could not get articles from Pocket for tag {tag}")

        json = response.json()
        articles = list()

        for entry in json["list"].values():
            given_url = entry["given_url"]
            item_id = entry["item_id"]
            articles.append(PocketItem(link=given_url, item_id=item_id))

        return (tag, articles)


    async def get_rss_feeds_from_tag(self, tags: set[str], access_token: str) -> dict[str, list[PocketItem]]:
        feeds = {}
        tasks = [self.get_rss_feed(tag, access_token) for tag in tags]
        results = await asyncio.gather(*tasks)
        for (title, article_urls) in results:
            feeds[title] = article_urls

        return feeds

    async def save_articles(self, links: dict[str, set[str]], access_token: str):
        url = f"{POCKET_BASE_URL}/v3/send?access_token={access_token}&consumer_key={settings.POCKET_CONSUMER_KEY}"
        for key in links.keys():
            if len(links[key]) == 0:
                continue

            actions = []
            for link in links[key]:
                actions.append({
                    "action": "add",
                    "url": link,
                    "tags": key
                })

            json_string = json.dumps(actions)
            logger.info(f"Saving articles: {json_string}")
            encoded = urllib.parse.quote(json_string)

            response = requests.get(url + f"&actions={encoded}")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=response.text)

    async def delete_articles(self, item_ids: dict[str, set[int]], access_token: str):
        url = f"{POCKET_BASE_URL}/v3/send?access_token={access_token}&consumer_key={settings.POCKET_CONSUMER_KEY}"
        for key in item_ids.keys():
            actions = []
            if len(item_ids[key]) == 0:
                continue

            for item_id in item_ids[key]:
                actions.append({
                    "action": "delete",
                    "item_id": item_id
                })
        

            json_string = json.dumps(actions)
            logger.info(f"Deleting articles: {json_string}")
            encoded = urllib.parse.quote(json_string)

            response = requests.get(url + f"&actions={encoded}")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=response.text)

