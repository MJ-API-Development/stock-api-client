
from datetime import datetime
from sqlalchemy import Column, String, inspect, Integer, Float

from src.databases.models.sql import Base, mysql_instance
from src.utils import date_from_timestamp


class Contacts(Base):
    """
        ORM Model for Contacts
    """
    __tablename__ = 'contact_messages'
    uuid = Column(String(16), index=True, nullable=True)
    contact_id = Column(String(16), primary_key=True, index=True)
    name = Column(String(128), index=True)
    email = Column(String(255), index=True)
    message = Column(String(255))
    timestamp = Column(Float, index=True)

    @property
    def datetime(self) -> datetime:
        return date_from_timestamp(self.timestamp)

    @classmethod
    def create_if_not_exists(cls):
        if not inspect(mysql_instance.engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=mysql_instance.engine)

