import datetime
import logging

import di
from domain.hello.datasources.hello import HelloDatasource
from pydantic import BaseModel
from utility.timestamp import timestamp


class GetHelloInfoOutput(BaseModel):
    message: str
    timestamp: int


@di.register
class GetHelloInfoCase:
    def __init__(self, hello: HelloDatasource, logger: logging.Logger):
        self.hello = hello
        self.logger = logger

    async def __call__(self) -> GetHelloInfoOutput:
        self.logger.info("Getting hello info")
        return GetHelloInfoOutput(
            message=self.hello.hello(),
            timestamp=timestamp(datetime.datetime.now()),
        )
