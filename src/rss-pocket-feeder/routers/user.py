from dataclasses import dataclass
from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from services.user import UserService
from utils import PocketAccessTokenDep

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()

@dataclass
class UserResponse:
    username: str
    pocket_access_token: str

@dataclass
class UserPostRequest:
    username: str

@router.get("/me")
async def get_user(access_token: PocketAccessTokenDep = None) -> UserResponse:
    if access_token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No token")

    user = await user_service.get_user(access_token)
    return UserResponse(username=user.username, pocket_access_token=user.pocket_access_token)

@router.post("")
async def save_user(user: UserPostRequest, access_token: PocketAccessTokenDep = None) -> UserResponse:
    if access_token is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="No token")

    saved_user = await user_service.save_user(
        username=user.username,
        pocket_access_token=access_token
    )

    return UserResponse(username=saved_user.username, pocket_access_token=saved_user.pocket_access_token)

