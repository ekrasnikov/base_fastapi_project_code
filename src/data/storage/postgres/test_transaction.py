# import pytest
#
# from app.settings import settings
# from data.storage.postgres.asyncpg_impl import AsyncpgPostgresDatabase
# from data.storage.postgres.exception import TransactionIsolationMismatch
# from data.storage.postgres.transaction import current_transaction
#
#
# async def test_transaction():
#     async def create_db():
#         db = AsyncpgPostgresDatabase()
#         await db.init(settings.postgres)
#         return db
#
#     db = await create_db()
#
#     async with db.transaction('read_committed'):
#         transaction = current_transaction.get()
#
#         async with db.transaction('read_committed'):
#             inner_transaction = current_transaction.get()
#             assert transaction is inner_transaction
#
#         transaction = current_transaction.get()
#         assert transaction
#
#     transaction = current_transaction.get()
#     assert transaction is None
#     await db.close()
#
#
# async def test_transaction_isolation_mismatch():
#     async def create_db():
#         db = AsyncpgPostgresDatabase()
#         await db.init(settings.postgres)
#         return db
#
#     db = await create_db()
#
#     with pytest.raises(TransactionIsolationMismatch):
#         async with db.transaction('read_committed'):
#             async with db.transaction('repeatable_read'):
#                 assert True
#
#     await db.close()
