import re
from datetime import datetime


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def date_from_timestamp(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp)


def date_to_timestamp(date: datetime) -> float:
    return date.timestamp()
