from pydantic import BaseModel


class Contacts(BaseModel):
    """
        ORM Model for Contacts
    """
    uuid: str | None
    contact_id: str | None
    name: str
    email: str
    message: str
    timestamp: float
