
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
    duration: int = Column(Integer)
    limit: int = Column(Integer)
    last_request_timestamp: float = Column(Float)
    requests_count: int = Column(Integer)

    def to_dict(self) -> dict[str, str]:
        return {
            "uuid": self.uuid,
            "api_key": self.api_key,
            "subscription_id": self.subscription_id,
            "duration": self.duration,
            "last_request_timestamp": self.last_request_timestamp,
            "requests_count": self.requests_count}
