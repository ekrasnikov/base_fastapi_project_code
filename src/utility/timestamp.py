from datetime import datetime


def timestamp(date: datetime) -> int:
    return int(date.timestamp() * 1000)
