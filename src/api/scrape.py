import json
from typing import Any

import aiohttp
from async_lru import alru_cache
from selectolax.parser import HTMLParser


@alru_cache(maxsize=32)
async def scrape_page(url: str, cache: str) -> dict[str, Any]:
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en",
        "_auth": "0",
        "_pinterest_sess": "TWc9PSZWdTN5b1FQZXdjYmU2eWVYTDhOY3RJZE92TEdLbUl4bTN0aWJmTUNnYkxHWjc5Sk4wKzM1SWdZOXJoV2hDUmRSTnJTenFyRDg1cFhCUlBYRmxaMWdBTGdwV08wM2toMHZmc0trYkxMcExUST0mQjV5VXhmZCtFZWJGZmV3RENhZ1pqWGs3aStrPQ==",
        "_routing_id": '"e9312c61-eb02-4261-983a-2e00fbb9c225"',
        "csrftoken": "2ad2559667502ad314ab7be233618b94",
        "sessionFunnelEventLogged": "1",
    }
    async with aiohttp.ClientSession(headers=headers) as session, session.get(url) as response:
        html = await response.text()

    parser = HTMLParser(html)
    data = {}
    for data_node in parser.css('script[type="application/json"]'):
        try:
            data.update(json.loads(data_node.text()))
        except TypeError:
            continue

    # from pathlib import Path
    # Path("data").mkdir(exist_ok=True)
    # with Path(f"data/{cache}.json").open("w") as f:  # noqa: ASYNC230, RUF100
    #     f.write(json.dumps(data, indent=4, ensure_ascii=False))

    return data
