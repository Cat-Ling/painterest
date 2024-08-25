from starlette.datastructures import URL


def get_proxied_url(url: str, /, *, base_url: str | URL) -> str:
    return f"{base_url}_/proxy?url={url}"
