import logging
from datetime import timedelta
from typing import Generic

import di
from domain.events.broker import EventBroker
from domain.events.models.event import Event, TEventData


class EventEmitter(Generic[TEventData]):  # type: ignore
    def __init__(self, event_broker: EventBroker, queue_name: str):
        self.event_broker = event_broker
        self.queue_name = queue_name
        self.logger = di.resolve(logging.Logger)()

    async def emit(self, event: Event[TEventData], delay: timedelta = timedelta()) -> None:
        self.logger.info(
            "Emitting event",
            extra={"event": event.model_dump(mode="json"), "queue": self.queue_name},
        )

        await self.event_broker.publish(self.queue_name, event.model_dump(mode="json"), delay)
