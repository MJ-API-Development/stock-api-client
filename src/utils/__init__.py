import re
from datetime import datetime
import string
import random

_char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def date_from_timestamp(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp)


def date_to_timestamp(date: datetime) -> float:
    return date.timestamp()


def get_api_key():
    return create_id(64)


def get_paypal_address():
    return "addrress@example.com"


def generate_key_api():
    return create_id(64)


def create_id(size: int = 16, chars: str = _char_set) -> str:
    """
        **create_id**
            create a random unique id for use as indexes in Database Models

    :param size: size of string - leave as default if you can
    :param chars: character set to create Unique identifier from leave as default
    :return: uuid -> randomly generated id
    """
    return ''.join(random.choice(chars) for _ in range(size))
