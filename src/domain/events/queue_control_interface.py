import abc
from datetime import timedelta


class QueueControlInterface(abc.ABC):
    @abc.abstractmethod
    async def ack(self): ...

    @abc.abstractmethod
    async def retry(self): ...

    @abc.abstractmethod
    async def delay(self, delay: timedelta): ...
