import abc

from app.settings import settings
from domain.environment.env import Env
from pydantic import BaseModel


class CacheModel(BaseModel, abc.ABC):
    @staticmethod
    def ttl():
        match settings.env:
            case Env.PYTEST:
                return 10
            case Env.LOCAL:
                return 60
            case Env.DEV:
                return 600
            case _:
                return 86400
