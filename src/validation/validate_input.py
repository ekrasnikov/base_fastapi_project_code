import contextlib

import fastapi.exceptions
import pydantic
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


@contextlib.contextmanager
def validate_input():
    try:
        yield
    except pydantic.ValidationError as pydantic_error:
        raise fastapi.exceptions.HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=pydantic_error.errors(),
        )
