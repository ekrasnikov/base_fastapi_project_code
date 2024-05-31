import enum
from typing import Type


def enum_to_sort_value(enum_cls: Type[enum.Enum], field_name: str) -> str:
    return " ".join(
        [
            "CASE",
            *[f"WHEN {field_name} = '{value.value}' THEN {index}" for index, value in enumerate(enum_cls)],
            f"ELSE {len(enum_cls)}",
            "END",
        ]
    )
