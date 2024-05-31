from pydantic import BaseModel


class EventPayload(BaseModel):
    __event_name__ = "event_payload"
