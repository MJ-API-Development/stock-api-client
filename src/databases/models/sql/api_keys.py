
from datetime import datetime
from typing import Self

from sqlalchemy import Column, String, inspect, Integer, Float
from src.databases.const import UUID_LEN, NAME_LEN, EMAIL_LEN, STR_LEN, CELL_LEN, API_KEY_LEN
from src.databases.models.sql import Base, mysql_instance, sessionType
from src.utils import date_from_timestamp


class APIKeys(Base):
    """

    """
    uuid: str = Column(String(UUID_LEN), index=True)
    api_key: str = Column(String(API_KEY_LEN), primary_key=True, index=True)
    subscription_id: str = Column(String(UUID_LEN))

    def to_dict(self) -> dict[str, str]:
        return {
            "uuid": self.uuid,
            "api_key": self.api_key,
            "subscription_id": self.subscription_id}
