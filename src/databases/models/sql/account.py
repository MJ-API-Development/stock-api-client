


from datetime import datetime
from typing import Self

from sqlalchemy import Column, String, inspect, Integer, Float
from src.databases.const import UUID_LEN, NAME_LEN, EMAIL_LEN, STR_LEN, CELL_LEN
from src.databases.models.sql import Base, mysql_instance, sessionType
from src.utils import date_from_timestamp


class Account(Base):
    """
        User Account ORM
    """
    __tablename__ = "accounts"
    uuid: str = Column(String(UUID_LEN), primary_key=True, index=True)
    first_name: str = Column(String(NAME_LEN), index=True)
    second_name: str = Column(String(NAME_LEN), index=True)
    surname: str = Column(String(NAME_LEN), index=True)
    email: str = Column(String(EMAIL_LEN), index=True, unique=True)
    cell: str = Column(String(CELL_LEN), index=True, unique=True)

    @property
    def names(self) -> str:
        return f"{self.first_name} {self.second_name} {self.surname}"

    @property
    def contact_details(self) -> str:
        return f"Cell: {self.cell}, Email: {self.email}"

    @classmethod
    async def get_by_uuid(cls, uuid: str, session: sessionType) -> Self:
        return session.query(cls).filter(cls.uuid == uuid).first()

    def to_dict(self) -> dict[str, str]:
        return {
            "uuid": self.uuid,
            "first_name": self.first_name,
            "second_name": self.second_name,
            "surname": self.surname,
            "email": self.email,
            "cell": self.cell}