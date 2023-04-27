from pydantic import BaseModel, Field


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

    class Config:
        title = "Subscriptions Model"


class PayPalSubscriptionModel(BaseModel):
    """
    captures subscription data from PayPalSubscriptions
    const subscription_data = {
        uuid, plan_id, paypal_id, billing_token, payer_id, subscription_id, facilitatorAccessToken
    }
    """
    uuid: str
    plan_id: str
    paypal_id: str
    billing_token: str
    payer_id: str
    subscription_id: str
    facilitatorAccessToken: str
    payment_method: str = "paypal"

    class Config:
        title = "PayPal Subscriptions Model"


class PlanModels(BaseModel):
    plan_id: str
    paypal_id: str
    plan_name: str
    charge_amount: float = Field(alias="Amount")

    @property
    def amount(self) -> float:
        return self.charge_amount

    def dict(self) -> dict[str, str | float]:
        return dict(plan_id=self.plan_id, paypal_id=self.paypal_id, plan_name=self.plan_name,
                    charge_amount=self.charge_amount, Amount=self.charge_amount)
