from typing import Annotated
from fastapi import APIRouter, Depends

from src.api.dependencies import HttpUoWDep, UOWDep, get_process
from src.services.payments import BasePaymentService
from src.schemas.payments import PaymentAddSchema

router = APIRouter(prefix="/payment")


@router.post("/deposit")
async def deposit(
    uow: UOWDep,
    data: PaymentAddSchema,
    http_uow: HttpUoWDep,
    service: Annotated[BasePaymentService, Depends(get_process)],
):
    payment = await service.deposite(uow, data, http_uow)
    return payment


@router.delete("/refund/{payment_id}")
async def refund(
    uow: UOWDep,
    payment_id: int,
    http_uow: HttpUoWDep,
    service: Annotated[BasePaymentService, Depends(get_process)],
):

    result = await service.refund(
        uow=uow,
        payment_id=payment_id,
        http_uow=http_uow,
    )

    return result
