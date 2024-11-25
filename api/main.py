from fastapi import FastAPI
from src.src import main

app = FastAPI(title="Social core", version="0.0.1") # openapi_url=None, docs_url=None, redoc_url=None

@app.get("/", tags=["home"])
async def status():
    return {"status": "okela"}

@app.get("/health", tags=["home"])
async def health():
    return {"status": "ok"}

@app.get("/facebook/search", tags=["search"])
async def search_facebook(q: str):
    return main(q)

