import enum

from data.storage.postgres.sorting import enum_to_sort_value


class TestEnum(str, enum.Enum):
    __test__ = False
    ZERO = "zero"
    ONE = "one"
    TWO = "two"


def test_enum_to_sort_value():
    assert enum_to_sort_value(TestEnum, "field") == (
        "CASE " "WHEN field = 'zero' THEN 0 " "WHEN field = 'one' THEN 1 " "WHEN field = 'two' THEN 2 " "ELSE 3 " "END"
    )
