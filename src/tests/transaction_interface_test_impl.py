class TestTransactionInterface:
    def __init__(self, txn_hash: str):
        self.txn_hash = txn_hash

    def hash(self) -> str:
        return self.txn_hash

    async def wait(self) -> None:
        pass
