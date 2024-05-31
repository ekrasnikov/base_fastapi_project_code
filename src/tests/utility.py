import datetime
import enum
import random
import uuid
from typing import Type, TypeVar
from unittest import mock
from uuid import UUID

EnumCls = TypeVar("EnumCls", bound=enum.Enum)


def make_object(methods: dict):
    """Creates repository-like object with defined methods"""
    return type("Repository", (object,), methods)


def resolved_value(result):
    """Shortcut to create coroutine that resolves to :param result:"""
    return mock.AsyncMock(return_value=result)


def returned_value(result):
    """Shortcut to create function that returns :param result:"""
    return mock.Mock(return_value=result)


def random_uint256() -> int:
    return random.randint(0, (2**256) - 1)


def random_enum(enum_cls: Type[EnumCls]) -> EnumCls:
    return random.choice(list(enum_cls))


def random_date(min_year: int = 1990, max_year: int = 2023):
    return datetime.datetime(
        random.randint(min_year, max_year),
        random.randint(1, 12),
        random.randint(1, 28),
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59),
    )


def random_uuid() -> UUID:
    return uuid.uuid4()
