from typing import Generic, Type, TypeVar

from domain.cache.cache import Cache
from domain.cache.models.cache_model import CacheModel

TValue = TypeVar("TValue", bound=CacheModel)


class TypedCache(Generic[TValue]):
    def __init__(self, value_type: Type[TValue], delegate: Cache):
        self.value_type = value_type
        self._delegate = delegate

    async def set(self, key: str, value: TValue) -> None:
        await self._delegate.set(key, value, self.value_type.ttl())

    async def get(self, key: str) -> TValue | None:
        data = await self._delegate.get(key)
        return self.value_type(**data) if data else None

    async def delete(self, key: str) -> None:
        await self._delegate.delete(key)
