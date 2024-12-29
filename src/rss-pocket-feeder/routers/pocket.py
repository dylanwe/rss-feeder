from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from services.user import UserService
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
import requests
import settings
import logging


router = APIRouter(prefix="/pocket", tags=["Pocket"])
user_service = UserService()
logger = logging.getLogger('uvicorn.error')
POCKET_BASE_URL = "https://getpocket.com"

@router.get("/start-auth")
async def start_auth() -> RedirectResponse:
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
    if response.status_code != HTTP_200_OK:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get request token.")
    data = response.json()
    request_token = data["code"]
    auth_url = f"{POCKET_BASE_URL}/auth/authorize?request_token={request_token}&redirect_uri={settings.REDIRECT_URI}?request_token={request_token}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(request_token: str) -> RedirectResponse:
    """
    Callback endpoint to handle Pocket's redirect after user authorization
    """
    logger.info(f"Callback with request token: {request_token}")
    access_token_url = f"{POCKET_BASE_URL}/v3/oauth/authorize"
    headers = {"X-Accept": "application/json"}
    payload = {
        "consumer_key": settings.POCKET_CONSUMER_KEY,
        "code": request_token
    }

    response = requests.post(access_token_url, json=payload, headers=headers)
    logger.info(response.text)
    if response.status_code != HTTP_200_OK:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get access token.")
    data = response.json()
    access_token = data["access_token"]
    username = data["username"]

    response = RedirectResponse(url="/dashboard")
    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="username", value=username)

    if not await user_service.get_user(access_token):
        await user_service.save_user(username, access_token)

    return response
