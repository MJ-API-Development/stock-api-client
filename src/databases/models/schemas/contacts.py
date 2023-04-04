import time

from pydantic import BaseModel


class Contacts(BaseModel):
    """
        ORM Model for Contacts

    """
    uuid: str | None
    contact_id: str | None
    name: str | None
    email: str | None
    message: str
    timestamp: float = time.monotonic()

# TODO add verification for contact fields
