import logging

from domain.hello.datasources.hello import HelloDatasource


class MockHelloDatasource(HelloDatasource):
    def __init__(self, logger: logging.Logger):
        # self.pg = pg
        self.logger = logger

    def hello(self) -> str:
        return "Hello! This is base code"
