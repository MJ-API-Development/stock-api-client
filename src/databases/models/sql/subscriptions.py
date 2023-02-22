from datetime import datetime
from sqlalchemy import Column, String, inspect, Integer, Float, ForeignKey, Text

from src.databases.const import UUID_LEN, NAME_LEN, EMAIL_LEN, STR_LEN
from src.databases.models.sql import Base, mysql_instance
from src.utils import date_from_timestamp


class Subscriptions(Base):
    subscription_id: str = Column(String(UUID_LEN), primary_key=True)
    screen_name: str = Column(String(NAME_LEN))
    plan: str = Column(String(NAME_LEN))
    _resource_list: str = Column(Text)

    @property
    def resource_list(self) -> list[str]:
        return self._resource_list.split(",")

    @resource_list.setter
    def resource_list(self, rs_list: list[str]):
        self._resource_list = ",".join(rs_list)

    def to_dict(self) -> dict[str, str | list[str]]:
        return {
            "subscription_id": self.subscription_id,
            "screen_name": self.screen_name,
            "plan": self.plan,
            "resources": self.resource_list
        }

