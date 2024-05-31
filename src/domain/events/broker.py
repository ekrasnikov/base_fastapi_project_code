import abc
from datetime import timedelta
from typing import AsyncIterator

from domain.events.processable_event import ProcessableEvent


class EventBroker(abc.ABC):
    @abc.abstractmethod
    async def listen(self, queue_name: str) -> AsyncIterator[ProcessableEvent]: ...

    @abc.abstractmethod
    async def publish(self, queue_name: str, message: dict, delay: timedelta = timedelta()) -> None: ...
