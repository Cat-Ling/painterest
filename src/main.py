import io
import os
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import aiohttp
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.pin import Pin, get_pin
from src.api.search import SearchResults, search


@asynccontextmanager
async def lifespan(_: FastAPI):
    global session

    development = os.environ.get("DEV")
    if development:
        from fastapi_tailwind import tailwind

        compile_tailwind = tailwind.compile(
            f"{static_files.directory}/css/tailwind.css", minify=True
        )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10))
    yield
    await session.close()
    if development:
        compile_tailwind.terminate()  # pyright: ignore[reportPossiblyUnboundVariable]


static_files = StaticFiles(directory="static")
app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/static", static_files, name="static")
templates = Jinja2Templates(directory="templates")
session: aiohttp.ClientSession = None  # pyright: ignore[reportAssignmentType]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, csrftoken: str | None = Query(None)):
    return templates.TemplateResponse("index.html", {"request": request, "csrftoken": csrftoken})


@app.get("/pin.json/{id:int}/", response_model=Pin)
async def pin_json(request: Request, id: int):
    return await get_pin(id, base_url=request.base_url)


@app.get("/pin/{id:int}/", response_class=HTMLResponse)
async def pin(request: Request, id: int):
    pin = await get_pin(id, base_url=request.base_url)
    return templates.TemplateResponse("pin.html", {"request": request, "pin": pin})


@app.get("/search/pins.json", response_model=SearchResults)
async def search_pins_api(
    request: Request,
    q: str = Query(...),
    csrftoken: str | None = Query(None),
    bookmarks: str | None = Query(None),
):
    if not q:
        raise HTTPException(status_code=400, detail="q: given parameter is empty.")
    return await search(q, bookmarks, csrftoken, request.base_url)


@app.get("/search/pins", response_class=HTMLResponse)
async def search_pins(
    request: Request,
    q: str = Query(..., alias="q"),
    bookmarks: str = Query("null"),
    csrftoken: str = Query("null"),
):
    url = f"{request.base_url}search/pins.json?q={q}&bookmarks={bookmarks}&csrftoken={csrftoken}"

    async with session.get(url) as response:
        data = await response.json()

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "results": data.get("results", []),
            "query": q,
            "bookmark": data.get("bookmark", "null"),
            "csrftoken": csrftoken,
        },
    )


@app.get("/_/proxy")
async def image_proxy(url: str = Query(...)):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            raise HTTPException(status_code=400, detail="Invalid protocol")
    except Exception:
        raise HTTPException(status_code=400, detail="Given URL is invalid.") from None

    allowed_hosts = ["pinimg.com", "i.pinimg.com", "s.pinimg.com", "pinterest.com"]
    if parsed_url.hostname not in allowed_hosts:
        raise HTTPException(
            status_code=400, detail="Unsupported host. Only Pinterest media can be proxied."
        )

    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(status_code=404, detail=f"Failed to fetch url: {url}")

        content_type = f"image/{'png' if url.endswith('.png') else 'jpeg'}"
        image_data = await response.read()

    return StreamingResponse(io.BytesIO(image_data), media_type=content_type)
