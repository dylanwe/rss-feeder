from fastapi import APIRouter, HTTPException
from typing import Tuple
from models import PocketItem
import asyncio
import requests
import settings
import json
import urllib.parse


pocket_router = APIRouter(prefix="/pocket", tags=["Pocket"])
POCKET_BASE_URL = "https://getpocket.com"

@pocket_router.get("/start-auth")
def start_auth():
    """
    Endpoint to start the authentication process
    """
    request_token_url = f"{POCKET_BASE_URL}/v3/oauth/request"
    headers = {"X-Accept": "application/json"}
    payload = {
        "consumer_key": settings.POCKET_CONSUMER_KEY,
        "redirect_uri": settings.REDIRECT_URI
    }

    response = requests.post(request_token_url, json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get request token.")
    data = response.json()
    request_token = data["code"]
    # Open this url in the browser to start the authentication process
    auth_url = f"{POCKET_BASE_URL}/auth/authorize?request_token={request_token}&redirect_uri={settings.REDIRECT_URI}?request_token={request_token}"
    return {"auth_url": auth_url, "request_token": request_token}


@pocket_router.get("/callback")
def callback(request_token: str):
    """
    Callback endpoint to handle Pocket's redirect after user authorization
    """
    print(request_token)
    access_token_url = f"{POCKET_BASE_URL}/v3/oauth/authorize"
    headers = {"X-Accept": "application/json"}
    payload = {
        "consumer_key": settings.POCKET_CONSUMER_KEY,
        "code": request_token
    }

    response = requests.post(access_token_url, json=payload, headers=headers)
    print(response.text)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get access token.")
    data = response.json()
    access_token = data["access_token"]
    username = data["username"]

    return {"access_token": access_token, "username": username}


async def get_rss_feed(tag: str) -> Tuple[str, list[PocketItem]]:
    url = f"{POCKET_BASE_URL}/v3/get"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "consumer_key": settings.POCKET_CONSUMER_KEY,
        "access_token": settings.POCKET_ACCESS_TOKEN,
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


async def get_rss_feeds_from_tag(tags: set[str]) -> dict[str, list[PocketItem]]:
    feeds = {}
    tasks = [get_rss_feed(tag) for tag in tags]
    results = await asyncio.gather(*tasks)
    for (title, article_urls) in results:
        feeds[title] = article_urls

    return feeds

async def save_articles(links: dict[str, set[str]]):
    url = f"{POCKET_BASE_URL}/v3/send?access_token={settings.POCKET_ACCESS_TOKEN}&consumer_key={settings.POCKET_CONSUMER_KEY}"
    for key in links.keys():
        actions = []
        for link in links[key]:
            actions.append({
                "action": "add",
                "url": link,
                "tags": key
            })
        json_string = json.dumps(actions)
        encoded = urllib.parse.quote(json_string)

        response = requests.get(url + f"&actions={encoded}")

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=response.text)

async def delete_articles(item_ids: dict[str, set[int]]):
    url = f"{POCKET_BASE_URL}/v3/send?access_token={settings.POCKET_ACCESS_TOKEN}&consumer_key={settings.POCKET_CONSUMER_KEY}"
    actions = []
    for key in item_ids.keys():
        for item_id in item_ids[key]:
            actions.append({
                "action": "delete",
                "item_id": item_id
            })

    json_string = json.dumps(actions)
    encoded = urllib.parse.quote(json_string)

    response = requests.get(url + f"&actions={encoded}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=response.text)

