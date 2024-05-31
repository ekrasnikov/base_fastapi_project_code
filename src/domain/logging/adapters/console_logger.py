import contextlib
import json
import logging.handlers
import time
import traceback
from typing import Any

from app.settings import Settings
from domain.environment.env import Env
from domain.logging.adapters.logger import LoggerAdapter, get_extra
from fastapi.encoders import jsonable_encoder


class ConsoleFormatter(logging.Formatter):
    def __init__(self, settings: Settings):
        self._settings = settings

    def format(self, record: logging.LogRecord) -> str:
        human_readable = self._settings.env == Env.LOCAL

        value = {
            "funcName": record.funcName,
            "module": record.module,
            "filename": record.filename,
            "lineno": record.lineno,
            "extra": get_extra(record),
        }

        if human_readable:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(record.created))
            result = [
                f"[{ts}.{record.msecs:.0f} +0000] [{record.process}] [{record.levelname}] {record.msg % record.args}\n",
                json.dumps(self._jsonable_encoder(value), indent=2),
            ]

            if record.exc_info:
                exc_cls, exc, tb = record.exc_info
                result.append("\n")
                result.extend(traceback.format_tb(tb))

            return "".join(result)
        else:
            return json.dumps(
                self._jsonable_encoder(
                    {
                        "level": record.levelname.lower(),
                        "message": record.msg % record.args,
                        "process": record.process,
                        **value,
                    }
                )
            )

    def _jsonable_encoder(self, value: Any) -> Any:
        def encode_exception(e: BaseException) -> dict[str, Any]:
            if hasattr(e, "to_json"):
                return e.to_json()
            return {
                "name": type(e).__name__,
                "args": e.args,
            }

        return jsonable_encoder(
            value,
            exclude_none=True,
            custom_encoder={BaseException: encode_exception},
        )


class ConsoleHandler(logging.StreamHandler):
    def __init__(self, settings: Settings):
        super().__init__()
        self.setFormatter(ConsoleFormatter(settings))


class ConsoleLoggerAdapter(LoggerAdapter):
    def __init__(self, settings: Settings):
        self._settings = settings

    @contextlib.contextmanager
    def setup(self):
        if self._settings.debug:
            level = logging.getLevelName("DEBUG")
        else:
            level = logging.getLevelName("INFO")

        logging.basicConfig(
            handlers=[ConsoleHandler(self._settings)],
            level=level,
        )
        yield
