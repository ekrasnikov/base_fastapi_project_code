from typing import Generic, TypeVar

from pydantic import BaseModel, SerializeAsAny

TEventData = TypeVar("TEventData", bound=BaseModel)


class Event(BaseModel, Generic[TEventData]):
    id: str
    event: str
    data: SerializeAsAny[TEventData]
    timestamp: float
    rollback: bool = False
