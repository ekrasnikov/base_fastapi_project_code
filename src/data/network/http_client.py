import abc
from typing import Mapping

import httpx


class HttpClient(abc.ABC):
    async def get(self, url: str, timeout: int = 10) -> httpx.Response:
        raise NotImplementedError

    async def post(
        self,
        url: str,
        json: Mapping,
        headers: Mapping,
        timeout: int = 10,
    ) -> httpx.Response:
        raise NotImplementedError
