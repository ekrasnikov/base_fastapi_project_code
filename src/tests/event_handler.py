from datetime import timedelta
from typing import Type

from domain.errors.base_exceptions import UnexpectedError
from domain.events.exceptions import RetryLater
from domain.events.handler import BatchingSettings, EventHandler
from domain.events.models.event import Event


class TestEventHandler(EventHandler):
    __test__ = False

    _ex_class: Type[Exception] | None = None

    def __init__(self, *, batch_id: str | None = None, fail: bool = False, delay: bool = False):
        self._batch_id = batch_id

        if fail:
            self._ex_class = UnexpectedError
        elif delay:
            self._ex_class = RetryLater

        self.received_events: list[Event] = []
        self.rolled_back_events: list[Event] = []

    def reset(self):
        self.received_events.clear()

    async def handle(self, event: Event):
        self.received_events.append(event)

        if self._ex_class:
            raise self._ex_class

    async def rollback(self, event: Event):
        self.received_events.append(event)
        self.rolled_back_events.append(event)

        if self._ex_class:
            raise self._ex_class

    async def handle_batch(self, events: list[Event]):
        self.received_events.extend(events)

        if self._ex_class:
            raise self._ex_class

    def batching_settings(self) -> BatchingSettings:
        return BatchingSettings(
            window=timedelta(seconds=0.1),
            max_size=1000,
        )

    def batch_id(self, event: Event) -> str | None:
        return self._batch_id
