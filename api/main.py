from fastapi import FastAPI
from src import fa

app = FastAPI(title="Social core", version="0.0.1") # openapi_url=None, docs_url=None, redoc_url=None

@app.get("/", tags=["home"])
async def status():
    return {"status": "okela"}

@app.get("/health", tags=["home"])
async def health():
    return {"status": "ok"}
@app.get("/facebook/search", tags=["search"])
async def search_facebook(q: str):
    return facebook.search(q)
# @app.get("/google/search", tags=["search"])
# async def search_google(q: str):
#     return google.search(q)
 
# @app.get("/youtube/search", tags=["search"])
# async def search_youtube(q:str, time_limit:str="last-hour"):
#     return youtube.search(q, time_limit)

