from pydantic import BaseModel
from src.databases.models.schemas.subscriptions import SubscriptionModel


class ApiKeysBaseModel(BaseModel):
    uuid: str
    api_key: str
    duration: int
    rate_limit: int
    is_active: bool
    subscription: SubscriptionModel

