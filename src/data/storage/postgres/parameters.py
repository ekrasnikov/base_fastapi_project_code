from typing import Any


class Parameters:
    def __init__(self, *params: Any):
        self._params = list(params)

    def __iter__(self):
        return iter(self._params)

    def add(self, value: Any) -> str:
        self._params.append(value)
        return f"${len(self._params)}"
