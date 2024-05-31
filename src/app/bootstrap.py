import json
import logging
import time
from contextlib import asynccontextmanager

from app.api.exceptions import ApiError
from app.settings import settings

# from data.cache.redis_cache import RedisCache
# from data.events.broker.rabbitmq.rabbitmq_impl import RabbitMQEventBroker
from data.hello.datasources.mock_db_hello import MockHelloDatasource

# from data.storage.postgres.asyncpg_impl import AsyncpgPostgresDatabase
# from data.storage.postgresql_database import PostgresDatabase
from di import container, resolve

# from domain.cache.cache import Cache
from domain.errors.app_exception import AppException
from domain.errors.base_exceptions import UnexpectedError
from domain.errors.base_exceptions import ValidationError as ApiValidationError
from domain.hello.datasources.hello import HelloDatasource

# from domain.events.broker import EventBroker
from domain.logging.adapters.console_logger import ConsoleLoggerAdapter
from domain.logging.adapters.logger import LoggerAdapter
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, StreamingResponse
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message


@asynccontextmanager
async def lifespan(app: FastAPI | None = None):
    container.register(HelloDatasource, MockHelloDatasource)

    logger_adapter = ConsoleLoggerAdapter(settings)
    container.register(LoggerAdapter, instance=logger_adapter)

    # pg = AsyncpgPostgresDatabase()
    # await pg.init(settings.postgres)
    # container.register(PostgresDatabase, instance=pg)

    # container.register(EventBroker, instance=RabbitMQEventBroker(settings))

    # redis_cache = RedisCache()
    # container.register(Cache, instance=redis_cache)

    with logger_adapter.setup():
        container.register(logging.Logger, instance=logging.getLogger("app"))
        yield

    # await pg.close()
    # await redis_cache.close()


async def log_request_and_response(request: Request, call_next):
    logger = resolve(logging.Logger)()
    body = await request.body()

    logger.info(
        "API request",
        extra={
            "api_request": {
                "method": request.method,
                "endpoint": request.url.path,
                "body": body,
                "headers": request.headers,
            },
        },
    )

    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    start = time.perf_counter()
    req = Request(request.scope, receive=receive)
    response: Response = await call_next(req)

    if isinstance(response, StreamingResponse):
        response_body = b""
        async for chunk in response.body_iterator:
            if isinstance(chunk, bytes):
                response_body += chunk
            elif isinstance(chunk, str):
                response_body += chunk.encode("utf-8")
    else:
        response_body = response.body

    logger.info(
        "API response",
        extra={
            "api_request": {
                "method": request.method,
                "endpoint": request.url.path,
                "execution_time_ms": round((time.perf_counter() - start) * 1000),
            },
            "api_response": response_body,
        },
    )

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


async def handle_exceptions(request: Request, call_next):
    # unable to use @app.exception_handler. See https://github.com/tiangolo/fastapi/discussions/8647
    logger = resolve(logging.Logger)()

    try:
        result = await call_next(request)
    except Exception as exc:
        if isinstance(exc, AppException):
            logger.error("Request failed with exception", extra={"error": exc})
            return await unicorn_app_exception_handler(request, exc)
        if isinstance(exc, ValidationError):
            logger.error("Request failed with exception", extra={"error": exc})
            return await unicorn_validation_exception_handler(request, exc)
        elif isinstance(exc, Exception):
            logger.error("Request failed with unexpected exception", extra={"error": exc})
            return await unicorn_base_exception_handler(request, exc)
        raise exc

    return result


async def unicorn_app_exception_handler(request: Request, exc: AppException):
    error = ApiError(exc)
    return ORJSONResponse(
        status_code=error.status_code,
        content=error.to_json(),
    )


async def unicorn_base_exception_handler(request: Request, exc: Exception):
    error = ApiError(UnexpectedError(debug=repr(exc)))
    return ORJSONResponse(
        status_code=error.status_code,
        content=error.to_json(),
    )


async def unicorn_validation_exception_handler(request: Request, exc: ValidationError):
    error = ApiError(ApiValidationError(payload=json.loads(exc.json()), debug=repr(exc)))

    return ORJSONResponse(
        status_code=error.status_code,
        content=error.to_json(),
    )
