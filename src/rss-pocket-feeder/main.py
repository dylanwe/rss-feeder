from fastapi import FastAPI
from pocket import pocket_router
from rss import rss_router

app = FastAPI()
app.include_router(pocket_router)
app.include_router(rss_router)

