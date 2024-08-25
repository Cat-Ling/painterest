from typing import Any, Self

from fastapi import HTTPException
from pydantic import BaseModel
from starlette.datastructures import URL

from src.api.scrape import scrape_page
from src.proxy import get_proxied_url


class PinUser(BaseModel):
    name: str
    username: str
    image: str
    followers: int

    @classmethod
    def from_data(cls, /, data: dict[str, Any] | None, *, base_url: str | URL) -> Self | None:
        if data is None:
            return None
        return cls(
            name=data.get("fullName") or "",
            username=data["username"],
            image=get_proxied_url(
                data.get("imageLargeUrl")
                or data.get("imageMediumUrl")
                or data.get("imageSmallUrl")
                or "",
                base_url=base_url,
            ),
            followers=data.get("followerCount", -1),
        )


class Pin(BaseModel):
    id: int
    tags: list[str]
    title: str | None
    description: str | None
    pin_url: str
    image: str
    # thumbnail: str
    source: str | None
    url: str | None
    pinner: PinUser | None
    creator: PinUser | None


async def get_pin(id: int, base_url: str | URL) -> Pin:
    url = f"https://www.pinterest.com/pin/{id}/"
    raw_data = await scrape_page(url=url, cache=f"pin-{id}")
    data: dict[str, Any] = (
        raw_data.get("response", {}).get("data", {}).get("v3GetPinQuery", {}).get("data")
    )
    if not data:
        raise HTTPException(status_code=404, detail=f"Pin not found: {id}")

    specs = ["orig", "736x", "564x", "474x", "236x", "170x", "136x136"]
    image = ""
    for spec in specs:
        value = data.get(f"imageSpec_{spec}")
        if value:
            image: str = value["url"]
            break
    pinner = data.get("pinner")
    creator = (
        data.get("nativeCreator")
        or (data.get("linkDomain") or {}).get("officialUser")
        or data.get("originPinner")
    )
    return Pin(
        id=id,
        tags=data.get("pinJoin", {}).get("visualAnnotation", []),
        title=data.get("title") or data.get("gridTitle"),
        description=(
            data.get("closeupUnifiedDescription") or data.get("description", "").strip() or None
        ),
        pin_url=f"/pin/{id}/",
        image=get_proxied_url(image, base_url=base_url),
        source=(data.get("richMetadata") or {}).get("siteName"),
        url=(data.get("richMetadata") or {}).get("url"),
        pinner=PinUser.from_data(pinner, base_url=base_url),
        creator=PinUser.from_data(creator, base_url=base_url),
    )
