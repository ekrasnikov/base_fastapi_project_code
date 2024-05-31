from datetime import datetime

from pydantic import BaseModel


class EventRecord(BaseModel):
    id: str
    event: str
    data: dict
    sent_at: datetime | None = None
    processed_at: datetime | None = None
    received_at: datetime
    rollback: bool | None = False
