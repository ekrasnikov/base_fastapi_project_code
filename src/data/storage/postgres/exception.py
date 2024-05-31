from domain.errors.app_exception import AppException


class TransactionIsolationMismatch(AppException):
    pass


class TransactionNotExists(AppException):
    pass
