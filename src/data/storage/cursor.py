import base64

import orjson
from domain.errors.common import InvalidCursor


def decode(cursor: str) -> dict:
    try:
        result = orjson.loads(base64.b64decode(cursor))
        assert isinstance(result, dict)
        return result
    except Exception as error:
        raise InvalidCursor() from error


def encode(cursor: dict) -> str:
    return base64.b64encode(orjson.dumps(cursor)).decode()
