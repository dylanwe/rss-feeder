from dataclasses import dataclass
from fastapi import APIRouter, HTTPException
from utils import PocketAccessTokenDep
from services.feed import FeedService
from models import GenericResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
import logging


router = APIRouter(prefix="/feeds", tags=["Feeds"])
feed_service = FeedService()
logger = logging.getLogger('uvicorn.error')

@dataclass
class FeedResponse:
    title: str
    url: str

@dataclass
class FeedPostRequest:
    rss_link: str

@router.get("")
async def get_feeds(access_token: PocketAccessTokenDep = None) -> list[FeedResponse]:
    if access_token is None:
        return []

    feeds = await feed_service.get_feeds(access_token)
    return [FeedResponse(title=feed.title, url=feed.url) for feed in feeds]


@router.post("")
async def save_rss_feed(request: FeedPostRequest, access_token: PocketAccessTokenDep = None) -> GenericResponse:
    logger.info(f"Saving feed: {request.rss_link}")

    if access_token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No token")

    try:
        await feed_service.save_feed(
            rss_link=request.rss_link,
            access_token=access_token
        )
        return GenericResponse(status="success")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save feed")

@router.patch("")
async def refresh_feeds(access_token: PocketAccessTokenDep = None):
    if access_token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No token")

    refresh_overview = await feed_service.refresh_feeds(access_token)
    return refresh_overview

@router.delete("")
async def delete_rss_feed(request: FeedPostRequest, access_token: PocketAccessTokenDep = None) -> GenericResponse:
    logger.info(f"Deleting feed: {request.rss_link}")

    if access_token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No token")

    try:
        await feed_service.delete_feed(
            rss_link=request.rss_link,
            access_token=access_token
        )
        return GenericResponse(status="success")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete feed")

