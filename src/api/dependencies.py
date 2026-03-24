from typing import Annotated

from fastapi import Depends, Request, Body

from src.services.payments import CashPaymentService, AcquiringService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork
from src.schemas.payments import PaymentAddSchema, PaymentType

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]


async def get_process(data: PaymentAddSchema):
    if data.type == PaymentType.CASH:
        return CashPaymentService()
    elif data.type == PaymentType.ACQUIRING:
        return AcquiringService()
