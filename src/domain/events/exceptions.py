from datetime import timedelta

from domain.errors.app_exception import AppException


class DuplicateEventError(AppException):
    pass


class EventNotRegisteredError(AppException):
    pass


class UnrecognizedEvent(AppException):
    pass


class RetryLater(AppException):
    def __init__(self, delay: timedelta = timedelta(seconds=5)):
        super().__init__()
        self.delay = delay
