from pydantic import BaseModel


class EventBrokerConfig(BaseModel):
    url: str
