import abc
import logging.handlers
from typing import Mapping


class LoggerAdapter(abc.ABC):
    pass


def get_extra(record: logging.LogRecord) -> Mapping:
    defaultRecord = logging.LogRecord("", 0, "", 0, "", None, None)
    defaultKeys = defaultRecord.__dict__.keys()
    return {key: value for key, value in record.__dict__.items() if key not in defaultKeys}
