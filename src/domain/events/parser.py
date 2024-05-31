import logging

import di
from domain.events.controllable_event import ControllableEvent
from domain.events.controllable_message import ControllableMessage
from domain.events.exceptions import UnrecognizedEvent
from domain.events.models.event import Event
from domain.events.registry import EventHandlerRegistry


class EventParser:
    def __init__(self, handler_registry: EventHandlerRegistry):
        self.registry = handler_registry
        self.logger = di.resolve(logging.Logger)()

    def parse(self, message: ControllableMessage) -> ControllableEvent:
        data = message.data
        event_type = self.registry.get_event(data["event"])

        if event_type is None:
            self.logger.error("No handler for event type", extra={"data": data})
            raise UnrecognizedEvent

        try:
            return ControllableEvent(
                event=Event(
                    id=data["id"],
                    event=data["event"],
                    timestamp=data["timestamp"],
                    data=event_type(**data["data"]),
                ),
                control=message.control,
            )
        except Exception as e:
            self.logger.error("Event validation failed", extra={"data": data, "error": e})
            raise
