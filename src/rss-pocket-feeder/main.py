from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from routers.user import router as user_router
from routers.feeds import router as feeds_router
from routers.pocket import router as pocket_router_v2
from utils import PocketAccessTokenDep

app = FastAPI()

api = APIRouter(prefix="/api/v2")
api.include_router(user_router)
api.include_router(feeds_router)
api.include_router(pocket_router_v2)
app.include_router(api)

@app.get("/")
async def login(access_token: PocketAccessTokenDep = None):
    if access_token is not None:
        return RedirectResponse("/dashboard")

    return FileResponse("src/rss-pocket-feeder/static/login.html")

@app.get("/dashboard")
async def dashboard(access_token: PocketAccessTokenDep = None):
    if access_token is None:
        return RedirectResponse("/")

    return FileResponse("src/rss-pocket-feeder/static/dashboard.html")

@app.get("/static/{file_path}")
async def read_static(file_path: str):
    return FileResponse(f"src/rss-pocket-feeder/static/{file_path}")

