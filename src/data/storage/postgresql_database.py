import abc
from datetime import timedelta
from typing import Any, AsyncContextManager, AsyncIterator, List, Mapping

import asyncpg
from data.storage.database import Database


class PostgresDatabase(Database):
    @abc.abstractmethod
    def transaction(self, isolation: str = "read_committed") -> AsyncContextManager: ...

    @abc.abstractmethod
    async def execute(self, query: str, *bindings, timeout: float | None = None): ...

    @abc.abstractmethod
    async def executemany(self, query: str, bindings, *, timeout: float | None = None): ...

    @abc.abstractmethod
    async def fetchrow(self, query: str, *bindings, timeout: float | None = None) -> Mapping | None: ...

    @abc.abstractmethod
    async def fetch(self, query: str, *bindings, timeout: float | None = None) -> List[Mapping]: ...

    @abc.abstractmethod
    async def fetchval(self, query: str, *bindings, timeout: float | None = None) -> Any | None: ...

    @abc.abstractmethod
    async def cursor(self, query: str, *args, step: int = 500) -> AsyncIterator[asyncpg.Record]: ...

    @abc.abstractmethod
    async def lock(self, name: str) -> AsyncContextManager: ...

    @abc.abstractmethod
    async def xact_lock(self, name: str, timeout: timedelta | None = None) -> bool | None: ...
