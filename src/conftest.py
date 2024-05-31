import asyncio
import logging
import os
from copy import deepcopy

import httpx
import pytest
from app.bootstrap import lifespan
from app.main import app

# from app.settings import settings
# from data.cache.redis_cache import RedisCache
from data.storage.postgresql_database import PostgresDatabase
from di import container
from domain.cache.cache import Cache
from domain.events.broker import EventBroker
from punq import MissingDependencyException

# from tests.asyncpg_test_impl import AsyncpgTestPostgresDatabase
# from tests.rabbitmq_test_impl import TestRabbitMQEventBroker

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def di():
    return container


# @pytest.fixture
# def db(di) -> AsyncpgTestPostgresDatabase:
#     return di.resolve(PostgresDatabase)


@pytest.fixture
def logger(di) -> logging.Logger:
    return di.resolve(logging.Logger)


# @pytest.fixture
# def cache(di) -> RedisCache:
#     return di.resolve(Cache)


@pytest.fixture(scope="session", autouse=True)
async def setup(di):
    os.environ["AIOCACHE_DISABLE"] = "1"

    async with lifespan(app):
        pass
        # pg = AsyncpgTestPostgresDatabase()
        # await pg.init(settings.postgres)

        # cache = RedisCache()
        # broker = TestRabbitMQEventBroker()

        # di.register(PostgresDatabase, instance=pg)
        # di.register(Cache, instance=cache)
        # di.register(EventBroker, instance=broker)


@pytest.fixture
async def client() -> httpx.AsyncClient:  # type: ignore
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
def broker(di):
    return di.resolve(EventBroker)


def pytest_runtest_teardown(item):
    try:
        pg = container.resolve(PostgresDatabase)
        cache = container.resolve(Cache)
    except MissingDependencyException:
        # Seems like setup() fixture has not been called.
        # E.g.: fixtures are not called for SKIPPED tests.
        return
    event_loop = item._request.getfixturevalue("event_loop")
    event_loop.run_until_complete(pg.rollback_transaction())
    event_loop.run_until_complete(cache.clear())


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "functional: Functional tests uses postgres or other integrations",
    )
    config.addinivalue_line(
        "markers",
        "unit: Unit test",
    )


@pytest.fixture(scope="function", autouse=True)
def reset_di_container_state():
    default_state = deepcopy(container.registrations)
    yield
    container.registrations = default_state
