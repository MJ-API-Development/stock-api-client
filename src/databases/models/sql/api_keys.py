from sqlalchemy import Column, String, Integer, Float, Boolean

from src.databases.const import UUID_LEN, API_KEY_LEN
from src.databases.models.sql import Base


class APIKeys(Base):
    """

    """
    __tablename__ = "eod_api_keys"
    uuid: str = Column(String(UUID_LEN), index=True)
    api_key: str = Column(String(API_KEY_LEN), primary_key=True, index=True)
    subscription_id: str = Column(String(UUID_LEN))
    duration: int = Column(Integer)
    limit: int = Column(Integer)
    is_active: bool = Column(Boolean, default=True)

    def to_dict(self) -> dict[str, str]:
        return {
            "uuid": self.uuid,
            "api_key": self.api_key,
            "subscription_id": self.subscription_id,
            "duration": self.duration,
            "limit": self.limit}
