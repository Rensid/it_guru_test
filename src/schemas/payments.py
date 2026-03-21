from pydantic import BaseModel

from src.models.models import PaymentType


class PaymentAddSchema(BaseModel):
    order_id: int
    amount: float
    type: PaymentType
