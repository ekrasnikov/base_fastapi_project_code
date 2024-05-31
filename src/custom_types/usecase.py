from typing import Callable, Type, TypeVar

from pydantic import BaseModel

Input = TypeVar("Input", bound=BaseModel)

Usecase = Type[Callable[[Input], None]]
