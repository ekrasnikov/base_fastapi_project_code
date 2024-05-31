import logging
from datetime import datetime
from typing import List, Type, get_args

import di
from domain.events.batch_processor import EventBatchProcessor
from domain.events.controllable_event import ControllableEvent
from domain.events.datasources.events import EventsDatasource
from domain.events.exceptions import DuplicateEventError
from domain.events.handler import EventHandler
from domain.events.models.base import EventPayload
from domain.events.models.event import Event, TEventData
from domain.events.models.event_handler_registry_item import EventHandlerRegistryItem
from domain.events.models.event_record import EventRecord


class EventHandlerRegistry:
    def __init__(self, event_handlers):
        self.handlers = dict()
        self.events = dict()
        self.events_ds = di.resolve(EventsDatasource)()
        self.register(event_handlers)
        self.logger = di.resolve(logging.Logger)()
        self.processor = EventBatchProcessor(self.logger)

    def register(self, handlers: List[Type[EventHandler]]):
        for handler in handlers:
            payload_class: Type[EventPayload] = get_args(handler.__orig_bases__[0])[0]
            event_name = payload_class.__event_name__

            if registered_event := self.get_event(event_name):
                if registered_event != payload_class:
                    raise DuplicateEventError(f"""
                        Event [{event_name}] was already defined by {registered_event}
                        so it cannot be defined again ({payload_class})
                    """)
            else:
                self.events[event_name] = payload_class

            if event_name not in self.handlers:
                self.handlers[event_name] = []

            self.handlers[event_name].append(EventHandlerRegistryItem(handler=handler, event_model=payload_class))

    def get_event(self, event: str) -> TEventData | None:
        return self.events.get(event)

    async def route(self, c_event: ControllableEvent):
        event = c_event.event

        if await self._is_event_processed(event):
            self.logger.warning("Event was already processed", extra={"event": event.model_dump()})
            await c_event.control.ack()
            return

        async with self.events_ds.tap(event_id=event.id) as event_record:
            if not event_record:
                self.logger.warning("Event not found", extra={"event": event.model_dump()})
                await c_event.control.ack()
                return

            for config in self.handlers.get(event.event, []):
                handler: EventHandler = di.resolve(config.handler)()
                await self.processor.handle(handler, c_event)

            event_record.processed_at = datetime.now()

    async def route_task(self, c_event: ControllableEvent):
        event = c_event.event

        self.logger.info(
            "Received task",
            extra={"event": event.model_dump(mode="json")},
        )

        for config in self.handlers.get(event.event, []):
            handler: EventHandler = di.resolve(config.handler)()
            await self.processor.handle(handler, c_event)

    async def _is_event_processed(self, event: Event) -> bool:
        record = EventRecord(**event.model_dump(), received_at=datetime.now(), sent_at=event.timestamp)
        return await self.events_ds.save(record) is None
