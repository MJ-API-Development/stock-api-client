from datetime import datetime
from sqlalchemy import Column, String, inspect, Integer, Float, ForeignKey, Text

from src.databases.const import UUID_LEN, NAME_LEN, EMAIL_LEN, STR_LEN
from src.databases.models.sql import Base, mysql_instance
from src.utils import date_from_timestamp


class Subscriptions(Base):
    subscription_id: str = Column(String(UUID_LEN), primary_key=True)
    screen_name: str = Column(String(NAME_LEN))
    plan: str = Column(String(NAME_LEN))
    resource_list: str = Column(Text)
