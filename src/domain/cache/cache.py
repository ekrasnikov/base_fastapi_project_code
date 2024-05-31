import abc
from typing import Any


class Cache(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> Any: ...

    @abc.abstractmethod
    async def set(self, key: str, value: Any, ttl: int) -> None: ...

    @abc.abstractmethod
    async def delete(self, key: str) -> None: ...

    @abc.abstractmethod
    async def clear(self): ...
