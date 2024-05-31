import os

from data.cache.config import RedisConfig
from data.events.broker.rabbitmq.config import EventBrokerConfig
from data.storage.postgres.config import PostgresConfig
from domain.environment.env import Env
from pydantic_settings import BaseSettings, SettingsConfigDict
from utility.fs import PROJECT_DIRECTORY

ENV = Env(os.getenv("ENV") or Env.LOCAL)


class Settings(BaseSettings):
    env: Env = ENV
    debug: bool = False

    postgres: PostgresConfig | None = None
    broker: EventBrokerConfig | None = None
    redis: RedisConfig | None = None

    model_config = SettingsConfigDict(
        env_file=(PROJECT_DIRECTORY / ".env", PROJECT_DIRECTORY / ".env.local"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    delete_incomplete_unboxing_tasks_interval: str = os.getenv("DELETE_INCOMPLETE_UNBOXING_TASKS_INTERVAL", "1 day")


settings = Settings()
