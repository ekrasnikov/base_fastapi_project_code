import asyncio
import functools
import signal
from typing import Awaitable, Callable

from app.bootstrap import lifespan


def async_run(func: Callable[..., Awaitable[None]]):
    async def routine(*args, **kwargs):
        loop = asyncio.get_running_loop()
        for signal_name in {signal.SIGINT, signal.SIGTERM}:
            loop.add_signal_handler(signal_name, lambda signum, frame: loop.stop())

        async with lifespan():
            return await func(*args, **kwargs)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(routine(*args, **kwargs))

    return wrapper
