from dataclasses import dataclass
from typing import Type


@dataclass
class EventHandlerRegistryItem:
    handler: Type
    event_model: Type
