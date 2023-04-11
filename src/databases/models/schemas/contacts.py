import re
import time

from pydantic import BaseModel, validator


# noinspection PyMethodParameters
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

    @validator('email')
    def validate_email(cls, email):
        """
        Validates the email address format
        """
        if email is not None and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        return email

    @validator('message')
    def validate_message(cls, message):
        """
         Validates the length and content of the message
        """
        if len(message) < 10 or len(message) > 500:
            raise ValueError("Message should be between 10 and 500 characters")

        # Regex pattern to match common attack patterns
        attack_pattern = r"(select|update|delete|drop|create|alter|insert|into|from|where|union|having|or|and|exec|script|javascript)"
        if re.search(attack_pattern, message, re.IGNORECASE):
            raise ValueError("Message contains common attack pattern")
        return message

    @validator('name')
    def validate_secure_name(cls, name):
        """
            Validates the name field using a more secure name validation
        """
        if len(name) < 2 or len(name) > 50:
            raise ValueError("Name should be between 2 and 50 characters")

        if not name.replace(' ', '').isalpha():
            raise ValueError("Name should only contain alphabetic characters and spaces")

        name_pattern = r"^[a-zA-Z]{1,25}([-']{1}[a-zA-Z]{1,25}){0,2}$"
        if not re.match(name_pattern, name):
            raise ValueError("Invalid Name")
        return name
