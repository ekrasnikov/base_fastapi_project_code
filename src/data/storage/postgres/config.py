from pydantic import BaseModel


class PostgresConfig(BaseModel):
    dsn: str
