import json
from typing import Any
from urllib.parse import quote

import aiohttp
from pydantic import BaseModel
from starlette.datastructures import URL

from src.proxy import get_proxied_url


class SearchUser(BaseModel):
    name: str | None
    username: str | None
    image: str | None


class SearchPin(BaseModel):
    pin_url: str
    url: str
    title: str | None
    content: Any
    image: str
    thumbnail: str
    source: Any
    pinner: SearchUser


class SearchResults(BaseModel):
    results: list[SearchPin]
    bookmark: str | None


async def search(
    query: str, bookmarks: str | None, token: str | None, base_url: str | URL
) -> SearchResults:
    query_data = {"options": {"query": query}}
    if bookmarks and bookmarks != "null":
        query_data["options"]["bookmarks"] = [bookmarks]  # pyright: ignore [reportArgumentType]

    headers = {}
    if token and token != "null":
        headers = {"csrftoken": token, "cookie": f"cookie:csrftoken={token}"}

    url = f"https://www.pinterest.com/resource/BaseSearchResource/get?data={quote(json.dumps(query_data))}"

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=headers)
        json_response = await response.json()

    results = []
    for res in json_response.get("resource_response", {}).get("data", {}).get("results", []):
        if res.get("type") != "story":
            pinner = res["pinner"]
            pin = SearchPin(
                pin_url=f"/pin/{res['id']}/",
                url=res.get("link") or f"/pin/{res['id']}/",
                title=res.get("title") or res.get("grid_title"),
                content=res.get("rich_summary") or res.get("display_description"),
                image=get_proxied_url(res["images"]["orig"]["url"], base_url=base_url),
                thumbnail=get_proxied_url(res["images"]["236x"]["url"], base_url=base_url),
                source=res.get("rich_summary") or res.get("site_name"),
                pinner=SearchUser(
                    name=pinner.get("full_name"),
                    username=pinner.get("username"),
                    image=get_proxied_url(
                        pinner.get("image_large_url")
                        or pinner.get("image_medium_url")
                        or pinner.get("image_small_url"),
                        base_url=base_url,
                    ),
                ),
            )
            results.append(pin)

    return SearchResults(
        results=results, bookmark=json_response.get("resource_response", {}).get("bookmark")
    )
