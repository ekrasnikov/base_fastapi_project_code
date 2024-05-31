import abc


class HelloDatasource(abc.ABC):
    @abc.abstractmethod
    def hello(self) -> str: ...
