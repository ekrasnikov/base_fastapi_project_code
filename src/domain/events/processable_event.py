import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import di
from domain.events.controllable_message import ControllableMessage


class ProcessableEvent:
    def __init__(self, message: ControllableMessage):
        self.message = message
        self.logger = di.resolve(logging.Logger)()

    @asynccontextmanager
    async def process(self) -> AsyncGenerator[ControllableMessage, None]:
        try:
            yield self.message
        except Exception as e:
            self.logger.error(
                "Exception while processing message",
                extra={"message_data": self.message.data, "error": e},
            )

            await self.message.control.retry()
