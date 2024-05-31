from typing import Any, Mapping

from app.settings import settings
from utility.formatting import split_camel_case


class AppException(Exception):
    def __init__(
        self,
        message: str | None = None,
        payload: Mapping | list[dict] | None = None,
        debug: Any = None,
    ):
        self.message = message or " ".join(split_camel_case(type(self).__name__)).title()
        self.payload = payload
        self.debug = debug

    @classmethod
    def code(cls) -> str:
        return cls.__name__

    def to_json(self) -> Mapping:
        return {
            "code": self.code(),
            "message": self.message,
            "payload": self.payload,
            "debug": self.debug if settings.debug else None,
        }
