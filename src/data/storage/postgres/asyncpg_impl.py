import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any, AsyncIterator, Iterable, List, cast
from uuid import UUID

import asyncpg
import orjson
from data.storage.postgres.advisory_lock import AdvisoryLock
from data.storage.postgres.config import PostgresConfig
from data.storage.postgres.exception import TransactionIsolationMismatch, TransactionNotExists
from data.storage.postgres.transaction import current_transaction
from data.storage.postgres.utils import json_encoder
from data.storage.postgresql_database import PostgresDatabase


class TransactionContext:
    __slots__ = ["__pool", "__connection_ctx", "__transaction", "isolation"]

    def __init__(self, pool: asyncpg.pool.Pool, isolation: str):
        self.__pool = pool
        self.__connection_ctx = None
        self.__transaction = None
        self.isolation = isolation

    async def __aenter__(self):
        self.__connection_ctx = self.__pool.acquire()
        connection = cast(asyncpg.connection.Connection, await self.__connection_ctx.__aenter__())
        self.__transaction = connection.transaction(isolation=self.isolation)
        try:
            await self.__transaction.__aenter__()
        except Exception:
            await asyncio.shield(self.__connection_ctx.__aexit__())
            raise

        return connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async def _close():
            try:
                await self.__transaction.__aexit__(exc_type, exc_val, exc_tb)
            finally:
                await self.__connection_ctx.__aexit__(exc_type, exc_val, exc_tb)

        await asyncio.shield(_close())


class AsyncpgPostgresDatabase(PostgresDatabase):
    __slots__ = ("__pool",)

    def __init__(self):
        self.__pool = None

    @property
    def pool(self) -> asyncpg.pool.Pool:
        assert self.__pool, "Pool is not initialized"
        return self.__pool

    @staticmethod
    def _connection_init():
        async def wrapper(connection: asyncpg.Connection):
            await connection.set_type_codec("json", schema="pg_catalog", encoder=json_encoder, decoder=orjson.loads)
            await connection.set_type_codec("jsonb", schema="pg_catalog", encoder=json_encoder, decoder=orjson.loads)
            await connection.set_type_codec("uuid", schema="pg_catalog", encoder=str, decoder=UUID)

        return wrapper

    def _connection_setup(self):
        async def wrapper(connection: asyncpg.pool.PoolConnectionProxy):
            pass

        return wrapper

    async def init(self, settings: PostgresConfig):
        assert settings.dsn
        self.__pool = await asyncpg.create_pool(
            dsn=settings.dsn,
            init=self._connection_init(),
            setup=self._connection_setup(),
            min_size=1,
            max_size=10,
        )

    async def close(self):
        await self.pool.close()
        self.__pool = None

    async def fetch(self, query: str, *args, timeout: float | None = None) -> List[asyncpg.Record]:
        method = getattr(current_transaction.get(), "fetch", self.pool.fetch)
        return await method(query, *args, timeout=timeout)

    async def fetchrow(self, query: str, *args, timeout: float | None = None) -> asyncpg.Record:
        method = getattr(current_transaction.get(), "fetchrow", self.pool.fetchrow)
        return await method(query, *args, timeout=timeout)

    async def fetchval(self, query: str, *args, timeout: float | None = None) -> Any:
        method = getattr(current_transaction.get(), "fetchval", self.pool.fetchval)
        return await method(query, *args, timeout=timeout)

    async def execute(self, query: str, *args, timeout: float | None = None) -> str:
        method = getattr(current_transaction.get(), "execute", self.pool.execute)
        return await method(query, *args, timeout=timeout)

    async def executemany(self, query: str, *args, timeout: float | None = None):
        method = getattr(current_transaction.get(), "executemany", self.pool.executemany)
        return await method(query, *args, timeout=timeout)

    async def cursor(self, query: str, *args, step: int = 500) -> AsyncIterator[asyncpg.Record]:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                cursor = await connection.cursor(query, *args)
                while rows := await cursor.fetch(step):
                    for row in rows:
                        yield row

    async def copy_records_to_table(
        self,
        table_name: str,
        *,
        records: Iterable[tuple],
        columns: list[str] | None = None,
        schema_name: str | None = None,
        timeout: float | int | None = None,
    ):
        async def _copy(conn, table_name, records, columns, schema_name, timeout):
            await conn.copy_records_to_table(
                table_name,
                records=records,
                columns=columns,
                schema_name=schema_name,
                timeout=timeout,
            )

        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await _copy(connection, table_name, records, columns, schema_name, timeout)

    @asynccontextmanager
    async def transaction(self, isolation: str = "read_committed"):
        transaction = current_transaction.get()

        if transaction and transaction._con._top_xact._isolation != isolation:
            raise TransactionIsolationMismatch

        if not transaction:
            async with TransactionContext(pool=self.pool, isolation=isolation) as conn:
                current_transaction.set(conn)

                try:
                    yield
                finally:
                    current_transaction.set(None)
        else:
            yield

    @asynccontextmanager
    async def lock(self, name: str):
        async with AdvisoryLock(self.pool, name):
            yield

    async def xact_lock(self, name: str, timeout: timedelta | None = None) -> bool:
        transaction = current_transaction.get()

        if not transaction:
            raise TransactionNotExists

        params = [hash(name)]
        query = "SELECT pg_advisory_xact_lock($1)"
        if timeout:
            params.append(int(timeout.total_seconds() * 1000))
            query = "SELECT pg_advisory_xact_lock_with_timeout($1, $2)"

        return await transaction.fetchval(query, *params) if timeout else True
