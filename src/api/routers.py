from typing import Annotated
from fastapi import APIRouter, Depends

from src.api.dependencies import UOWDep, get_process
from src.services.payments import BasePaymentService
from src.schemas.payments import PaymentAddSchema

router = APIRouter(prefix="/payment")


@router.post("/deposit")
async def deposit(
    uow: UOWDep,
    data: PaymentAddSchema,
    service: Annotated[BasePaymentService, Depends(get_process)],
):
    payment = await service.deposite(uow, data)
    return payment


@router.delete("/refund/{payment_id}")
async def refund(uow: UOWDep, payment_id: int):
    pass
