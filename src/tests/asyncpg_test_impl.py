import asyncio
import contextlib
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Mapping

import asyncpg.transaction
from data.storage.postgres.asyncpg_impl import AsyncpgPostgresDatabase, TransactionContext
from data.storage.postgres.transaction import current_transaction


class PoolProxy:
    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool
        self.tx_ctx = None
        self.tx_conn = None

    def __getattr__(self, item):
        if item in {"fetch", "fetchrow", "fetchval", "execute", "executemany"}:
            return self.operation_proxy(item)
        elif item == "acquire":  # call when cursor is using
            return lambda: contextlib.nullcontext(self.tx_conn)

        return getattr(self._pool, item)

    async def start_transaction(self):
        assert self.tx_ctx is None, "Transaction already started"

        self.tx_ctx = TransactionContext(pool=self._pool, isolation="read_committed")
        self.tx_conn = await self.tx_ctx.__aenter__()

    def operation_proxy(self, func_name: str):
        async def wrapper(*args, **kwargs):
            if self.tx_conn is None:
                await self.start_transaction()

            func = getattr(self.tx_conn, func_name)
            return await func(*args, **kwargs)

        return wrapper


class AsyncpgTestPostgresDatabase(AsyncpgPostgresDatabase):
    pool_proxy = None

    @property
    def pool(self) -> PoolProxy:
        if not self.pool_proxy:
            self.pool_proxy = PoolProxy(super().pool)
        return self.pool_proxy

    @asynccontextmanager
    async def transaction(self, isolation: str = "read_committed"):
        if self.pool.tx_ctx is None:
            await self.pool.start_transaction()
        current_transaction.set(self.pool.tx_conn)
        yield self.pool.tx_conn

    async def rollback_transaction(self):
        if self.pool.tx_ctx is None:
            return

        async def _close():
            try:
                await self.pool.tx_ctx.__aexit__(True, None, None)
            finally:
                self.pool.tx_ctx = None
                self.pool.tx_conn = None

        await asyncio.shield(_close())

    async def insert_into_table(self, table_name: str, data: List[Mapping]) -> List[Mapping]:
        if not data:
            return []

        stmt_args: List[Any] = []
        stmt_values: List[str] = []
        table_attributes = set()

        for data_item in data:
            table_attributes.update({key for key in data_item.keys()})

        i = 1
        for item in data:
            item_data = [item.get(attr) for attr in table_attributes]
            stmt_args.extend(item_data)
            stmt_values.append(f"({','.join(f'${i + j}' for j in range(len(item_data)))})")
            i += len(item_data)

        stmt = f"""
            INSERT INTO {table_name} ({', '.join(table_attributes)})
            VALUES {','.join(stmt_values)}
            RETURNING *
        """
        result = await self.fetch(stmt, *stmt_args)
        return [{**row} for row in result]

    async def insert_into_tables(self, data: Dict[str, List[Mapping]]) -> Dict[str, List[Mapping]]:
        result = {}
        for table_name, records in data.items():
            result[table_name] = await self.insert_into_table(table_name, records)
        return result

    async def truncate_table(self, table_name: str) -> None:
        await self.execute(f"TRUNCATE TABLE {table_name} CASCADE")
