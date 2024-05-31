import enum


class Env(str, enum.Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"
    PYTEST = "pytest"
    LOCAL = "local"
