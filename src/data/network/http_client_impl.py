from typing import Mapping

import httpx
import tenacity
from data.network.http_client import HttpClient


def is_retriable(error: Exception) -> bool:
    return (
        isinstance(error, httpx.TransportError)
        or isinstance(error, httpx.HTTPStatusError)
        and (error.response.status_code >= 500 or error.response.status_code == 429)
    )


def is_forbidden(error: Exception) -> bool:
    return isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 403


class HttpClientImpl(HttpClient):
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=0.5),
        retry=tenacity.retry_if_result(is_retriable),
        reraise=True,
    )
    async def get(self, url: str, timeout: int = 10) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=0.5),
        retry=tenacity.retry_if_result(is_retriable),
        reraise=True,
    )
    async def post(self, url: str, json: Mapping, headers: Mapping, timeout: int = 10) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=json, headers=headers)
            return r
