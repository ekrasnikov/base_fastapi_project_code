import abc
from dataclasses import dataclass
from datetime import timedelta
from typing import Generic

from domain.events.models.event import Event, TEventData


@dataclass
class BatchingSettings:
    window: timedelta
    max_size: int


class EventHandler(Generic[TEventData], abc.ABC):  # type: ignore
    @abc.abstractmethod
    async def handle(self, event: Event[TEventData]): ...

    async def rollback(self, event: Event[TEventData]):
        raise NotImplementedError

    async def handle_batch(self, events: list[Event[TEventData]]):
        raise NotImplementedError

    def batching_settings(self) -> BatchingSettings:
        return BatchingSettings(
            window=timedelta(seconds=1),
            max_size=1000,
        )

    def batch_id(self, event: Event[TEventData]) -> str | None:
        return None
