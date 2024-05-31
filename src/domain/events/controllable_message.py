from dataclasses import dataclass

from domain.events.queue_control_interface import QueueControlInterface


@dataclass
class ControllableMessage:
    data: dict
    control: QueueControlInterface
