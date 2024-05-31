# import asyncio
#
# from domain.cache.cache import Cache
#
# cache_key = 'SUPER_KEY'
#
#
# async def test_redis_cache_successful(di):
#     cache = di.resolve(Cache)
#     test_obj = {'key': 'value'}
#     await cache.set(key=cache_key, value=test_obj, ttl=2)
#     value = await cache.get(cache_key)
#     assert value['key'] == str(test_obj['key'])
#
#
# async def test_redis_cache_key_expired(di):
#     cache = di.resolve(Cache)
#     test_obj = {'key': 'value'}
#
#     await cache.set(key=cache_key, value=test_obj, ttl=1)
#     await asyncio.sleep(1.5)
#
#     value = await cache.get(cache_key)
#     assert value is None
#
#
# async def test_redis_delete_key(di):
#     cache: Cache = di.resolve(Cache)
#     test_obj = {'key': 'value'}
#     await cache.set(key=cache_key, value=test_obj, ttl=1000)
#
#     await cache.delete(cache_key)
#
#     value = await cache.get(cache_key)
#     assert value is None
