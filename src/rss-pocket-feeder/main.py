from fastapi import FastAPI
from fastapi.responses import FileResponse
from pocket import pocket_router
from rss import rss_router

app = FastAPI()
app.include_router(pocket_router)
app.include_router(rss_router)

@app.get("/")
async def read_root():
    return FileResponse("src/rss-pocket-feeder/static/index.html")

@app.get("/static/{file_path}")
async def read_static(file_path: str):
    return FileResponse(f"src/rss-pocket-feeder/static/{file_path}")

