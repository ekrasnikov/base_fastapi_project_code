import abc
from typing import AsyncGenerator, AsyncIterator

from domain.events.models.event_record import EventRecord


class EventsDatasource(abc.ABC):
    @abc.abstractmethod
    async def save(
        self,
        event: EventRecord,
    ) -> EventRecord | None: ...

    @abc.abstractmethod
    async def get_by_id(self, id: str) -> EventRecord | None: ...

    @abc.abstractmethod
    async def tap(self, event_id: str) -> AsyncGenerator[EventRecord | None, None]: ...

    @abc.abstractmethod
    async def get_multiple(
        self,
        processed: bool | None = None,
        event_types: list[str] | None = None,
    ) -> AsyncIterator[EventRecord]: ...

    @abc.abstractmethod
    async def set_unprocessed(
        self,
        event_id: str,
    ) -> None: ...
