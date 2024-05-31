from typing import Any

import orjson
import redis.asyncio as redis
from app.settings import settings
from domain.cache.cache import Cache
from domain.environment.env import Env


class RedisCache(Cache):
    def __init__(self):
        self._connection = None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        if not self._connection:
            await self._init()

        await self._connection.set(name=key, value=orjson.dumps(value.model_dump(mode="json")), ex=ttl)

    async def get(self, key: str) -> Any:
        if not self._connection:
            await self._init()

        value = await self._connection.get(key)
        return orjson.loads(value) if value is not None else None

    async def delete(self, key: str) -> None:
        if not self._connection:
            await self._init()

        await self._connection.delete(key)

    async def clear(self):
        if not self._connection:
            return

        if settings.env not in [Env.PYTEST]:
            return

        keys = await self._connection.keys()
        if keys:
            await self._connection.delete(*keys)

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _init(self):
        assert settings.redis

        pool = redis.ConnectionPool.from_url(f"redis://{settings.redis.host}?encoding=utf-8")
        self._connection = redis.Redis(connection_pool=pool, auto_close_connection_pool=True)
