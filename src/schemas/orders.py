from enum import Enum

from pydantic import BaseModel


class OrderPaymentStatus(str, Enum):
    NOT_PAID = "not_paid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class OrderSchema(BaseModel):
    status: OrderPaymentStatus
