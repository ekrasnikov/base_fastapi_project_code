import asyncio
from typing import AsyncIterator, Awaitable, Callable, Generic, TypeVar

TValue = TypeVar("TValue")


class ConcurrentProcessor(Generic[TValue]):
    @classmethod
    async def run(
        self,
        source: AsyncIterator[TValue],
        process: Callable[[TValue], Awaitable[None]],
        *,
        max_queue_size: int = 10000,
        max_concurrency: int = 10,
    ):
        queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)

        async def queue_worker(name: str, queue: asyncio.Queue) -> None:
            while True:
                item: TValue = await queue.get()
                while True:
                    try:
                        await process(item)
                        break
                    except Exception as error:
                        print("EXCEPTION:", repr(error))
                        await asyncio.sleep(1)
                queue.task_done()

        workers = [asyncio.create_task(queue_worker(f"worker-{i}", queue)) for i in range(max_concurrency)]

        async for item in source:
            await queue.put(item)

        await queue.join()

        for worker in workers:
            worker.cancel()

        await asyncio.gather(*workers, return_exceptions=True)
