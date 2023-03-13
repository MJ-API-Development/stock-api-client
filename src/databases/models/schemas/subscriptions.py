
from pydantic import BaseModel


class SubscriptionModel(BaseModel):
    """Basic Subscription Model Schema - can be used to create new schema, update a schema and get schema data"""
    subscription_id: str | None
    plan_id: str | None
    uuid: str | None = None
    time_subscribed: float | None = None
    payment_day: str | None = None
    _is_active: bool | None = None
    api_requests_balance: int | None = None
    approval_url: str | None = None
    paypal_id: str | None = None
