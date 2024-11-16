from fastapi import APIRouter, HTTPException
from typing import Tuple
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


async def get_rss_feed(tag: str) -> Tuple[str, set[str]]:
    try:
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
        json = response.json()
        articles = set()

        for entry in json["list"].values():
            articles.add(entry["given_url"])

        return (tag, articles)
    except Exception as e:
        print(f"Failed to get RSS feed for tag {tag}")
        print(e)
        return (tag, set())



async def get_rss_feeds_from_tag(tags: set[str]) -> dict[str, Tuple[str, set[str]]]:
    feeds = {}
    for tag in tags:
        (title, article_urls) = await get_rss_feed(tag)
        feeds[title] = article_urls

    return feeds

async def save_articles(links: set[str], tag: str):
    url = f"{POCKET_BASE_URL}/v3/send?access_token={settings.POCKET_ACCESS_TOKEN}&consumer_key={settings.POCKET_CONSUMER_KEY}"
    actions = []
    for link in links:
        actions.append({
            "action": "add",
            "url": link,
            "tags": tag
        })

    json_string = json.dumps(actions)
    encoded = urllib.parse.quote(json_string)

    requests.get(url + f"&actions={encoded}")

