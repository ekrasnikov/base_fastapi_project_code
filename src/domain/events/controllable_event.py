from dataclasses import dataclass

from domain.events.models.event import Event
from domain.events.queue_control_interface import QueueControlInterface


@dataclass
class ControllableEvent:
    event: Event
    control: QueueControlInterface
