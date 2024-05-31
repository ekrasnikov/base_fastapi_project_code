from typing import Mapping

import httpx
from data.network.http_client import HttpClient


class TestHttpClientImpl(HttpClient):
    __test__ = False

    def __init__(self, resources: dict[str, bytes]):
        self._resources = resources

    async def get(self, url: str, timeout: int = 10) -> httpx.Response:
        result = self._resources.get(url, None)

        if result is not None:
            return httpx.Response(content=result, status_code=200)

        raise httpx.HTTPStatusError(
            "Not found",
            request=httpx.Request("GET", str(url)),
            response=httpx.Response(404),
        )

    async def post(
        self,
        url: str,
        json: Mapping,
        headers: Mapping,
        timeout: int = 10,
    ) -> httpx.Response:
        result = self._resources.get(url, None)

        if result is not None:
            return httpx.Response(content=result, status_code=200)

        raise httpx.HTTPStatusError(
            "Not found",
            request=httpx.Request("GET", str(url)),
            response=httpx.Response(404),
        )
