import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable

from domain.events.controllable_event import ControllableEvent
from domain.events.exceptions import RetryLater
from domain.events.handler import EventHandler
from domain.events.models.event import Event


class EventBatch:
    flush_task: asyncio.Task | None = None

    def __init__(self, handler: EventHandler, logger: logging.Logger, events: list[ControllableEvent] = []):
        self.handler = handler
        self.logger = logger
        self.batching_window = handler.batching_settings().window

        self.events: list[ControllableEvent] = []
        for event in events:
            self.add(event)

    def add(self, event: Event):
        self.events.append(event)

        if self.flush_task is None:
            self.flush_task = self._schedule_flush(datetime.now() + self.batching_window)

    def _schedule_flush(self, time: datetime) -> asyncio.Task:
        async def func():
            delay = time - datetime.now()
            if delay > timedelta():
                await asyncio.sleep(delay.total_seconds())
            await self._flush()

        return asyncio.create_task(func())

    async def _flush(self):
        events = [*self.events]
        self.events.clear()

        now = datetime.now()

        try:
            await self.handler.handle_batch(
                [event.event for event in events],
            )
            for event in events:
                await event.control.ack()

        except Exception as e:
            if isinstance(e, RetryLater):
                self.logger.info(
                    f"Event batch will be retried in {e.delay}",
                    extra={
                        "events": [event.event.model_dump(mode="json") for event in events],
                    },
                )
                for event in events:
                    await event.control.delay(e.delay)
            else:
                self.logger.error(
                    "Exception while handling event batch",
                    extra={
                        "events": [event.event.model_dump(mode="json") for event in events],
                        "error": e,
                    },
                )
                for event in events:
                    await event.control.retry()

        if len(self.events) > 0:
            self.flush_task = self._schedule_flush(now + self.batching_window)
        else:
            self.flush_task = None


class EventBatchRegistry:
    def __init__(self) -> None:
        self.batches: dict[str, EventBatch] = {}

        self.cleanup_task = asyncio.create_task(
            self._cleanup_task(),
        )

    def get(self, key: str, factory: Callable[[], EventBatch]) -> EventBatch:
        if key in self.batches:
            return self.batches[key]

        batch = self.batches[key] = factory()
        return batch

    async def _cleanup_task(self):
        while True:
            await asyncio.sleep(1)
            self._cleanup()

    def _cleanup(self):
        self.batches = {key: batch for key, batch in self.batches.items() if batch.flush_task is not None}


class EventBatchProcessor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.batches = EventBatchRegistry()

    async def handle(self, handler: EventHandler, event: ControllableEvent):
        batch_id = handler.batch_id(event.event)

        if batch_id is None:
            await self._handle_immediate(handler, event)
            return

        batch = self.batches.get(
            f"{id(handler)}:{batch_id}",
            lambda: EventBatch(handler, self.logger),
        )
        batch.add(event)

    async def _handle_immediate(self, handler: EventHandler, event: ControllableEvent):
        try:
            await self._call_handler(handler, event.event)
            await event.control.ack()

        except RetryLater as e:
            await event.control.delay(e.delay)
            raise
        except Exception:
            await event.control.retry()
            raise

    async def _call_handler(self, handler: EventHandler, event: Event):
        try:
            if event.rollback:
                await handler.rollback(event)
            else:
                await handler.handle(event)

        except RetryLater as e:
            self.logger.info(
                f"Event will be retried after {e.delay}",
                extra={"event": event.model_dump(mode="json")},
            )
            raise
        except Exception as e:
            self.logger.error(
                "Exception while handling event",
                extra={"event": event.model_dump(mode="json"), "error": e},
            )
            raise
