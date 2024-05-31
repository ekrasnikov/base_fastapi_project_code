import datetime
from typing import Generic, TypeVar
from uuid import uuid4

from app.settings import settings
from domain.events.broker import EventBroker
from domain.events.emitter import EventEmitter
from domain.events.models.event import Event
from domain.tasks.models.task_payload import TaskPayload

TPayload = TypeVar("TPayload", bound=TaskPayload)


class TaskEmitter(Generic[TPayload]):
    def __init__(self, event_broker: EventBroker):
        self.emitter = EventEmitter(event_broker, settings.task_queue_name)

    async def emit(
        self,
        task: TPayload,
        rollback: bool = False,
        delay: datetime.timedelta = datetime.timedelta(),
    ) -> None:
        await self.emitter.emit(
            Event(
                id=str(uuid4()),
                event=task.__event_name__,
                data=task,
                timestamp=datetime.datetime.now().timestamp(),
                rollback=rollback,
            ),
            delay,
        )
