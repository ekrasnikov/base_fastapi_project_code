from datetime import timedelta

from domain.events.broker import EventBroker
from domain.events.queue_control_interface import QueueControlInterface


class TestRabbitMQEventBroker(EventBroker):
    __test__ = False

    def __init__(self) -> None:
        self._published: list[dict] = []

    async def listen(self, queue_name: str):
        pass

    async def publish(self, queue_name: str, message: dict, delay: timedelta = timedelta()) -> None:
        self._published.append(
            {
                "queue_name": queue_name,
                "message": message,
                "delay": delay,
            }
        )

    def published_messages(self):
        result = [*self._published]
        self._published.clear()
        return result


class TestQueueControlInterface(QueueControlInterface):
    __test__ = False

    status: str = ""

    async def ack(self):
        if self.status == "":
            self.status = "acked"

    async def retry(self):
        if self.status == "":
            self.status = "retried"

    async def delay(self, delay: timedelta):
        if self.status == "":
            self.status = "delayed"
