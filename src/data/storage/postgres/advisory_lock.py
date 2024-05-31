from data.storage.postgres.exception import TransactionNotExists
from data.storage.postgres.transaction import current_transaction


class AdvisoryLock:
    def __init__(self, name: str):
        self.name = hash(name)
        self.transaction = current_transaction.get()

    async def __aenter__(self):
        if not self.transaction:
            raise TransactionNotExists

        await self.transaction.execute("SELECT pg_advisory_lock($1)", self.name)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transaction.execute("SELECT pg_advisory_unlock($1)", self.name)
