from domain.errors.app_exception import AppException


class ValidationError(AppException):
    pass


class UnexpectedError(AppException):
    pass


class InvalidPayload(AppException):
    pass


class Forbidden(AppException):
    pass


class Unauthorized(AppException):
    pass
