from typing import Dict, List, Mapping

from domain.errors.app_exception import AppException
from fastapi import status

EXCEPTION_TO_STATUS_CODE = {
    "UnexpectedError": status.HTTP_500_INTERNAL_SERVER_ERROR,
    "InvalidPayload": status.HTTP_400_BAD_REQUEST,
    "NotFound": status.HTTP_404_NOT_FOUND,
    "Unauthorized": status.HTTP_401_UNAUTHORIZED,
    "Forbidden": status.HTTP_403_FORBIDDEN,
    "Conflict": status.HTTP_409_CONFLICT,
    "ValidationError": status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def get_status_code(exc: "AppException") -> int:
    if exc.code() in EXCEPTION_TO_STATUS_CODE:
        return EXCEPTION_TO_STATUS_CODE[exc.code()]

    for base in type(exc).__bases__:
        if base.__name__ in EXCEPTION_TO_STATUS_CODE:
            return EXCEPTION_TO_STATUS_CODE[base.__name__]

    raise Exception(f"No status found for {exc}")


def exception_schema(exceptions: List["AppException"]):
    responses: Dict[int, Dict] = {}

    for exc in exceptions:
        add_exception_to_schemas_dict(responses, exc)

    return responses


def add_exception_to_schemas_dict(schemas: Dict, exception: AppException):
    status_code = get_status_code(exception)
    if status_code in schemas:
        schemas[status_code]["content"]["application/json"]["examples"].update(exception_to_example(exception))
        return

    schemas.update(exception_to_response_schema(exception))


def exception_to_response_schema(exception: AppException) -> Dict:
    schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "title": "Error code",
            },
            "message": {
                "type": "string",
                "title": "Error description",
            },
            "payload": {
                "type": "object",
                "title": "Additional information",
            },
            "debug": {
                "type": "string",
                "title": "Traceback or other internal information (available only on dev environments)",
            },
        },
    }
    status_code = get_status_code(exception)
    return {
        status_code: {
            "content": {
                "application/json": {
                    "schema": schema,
                    "examples": exception_to_example(exception),
                },
            },
        },
    }


def exception_to_example(exception: AppException):
    code = exception.code()
    return {
        code: {
            "value": {
                "code": code,
                "message": exception.message,
            },
        },
    }


class ApiError:
    def __init__(self, original_error: AppException):
        self._original_error = original_error

    @property
    def status_code(self) -> int:
        return get_status_code(self._original_error)

    @property
    def code(self) -> str:
        return type(self._original_error).__name__

    def to_json(self) -> Mapping:
        return self._original_error.to_json()
