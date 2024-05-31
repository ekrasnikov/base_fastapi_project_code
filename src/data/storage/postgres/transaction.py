import functools
from contextvars import ContextVar
from typing import Callable, TypeVar

import asyncpg
from data.storage.postgresql_database import PostgresDatabase
from di import container

_T = TypeVar("_T")

current_transaction: ContextVar[asyncpg.connection.Connection | None] = ContextVar(
    "current_transaction",
    default=None,
)


def transaction(isolation: str = "read_committed") -> Callable[[_T], _T]:
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            pg = container.resolve(PostgresDatabase)
            async with pg.transaction(isolation):
                return await func(*args, **kwargs)

        return wrapped

    return wrapper
