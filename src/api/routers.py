from fastapi import APIRouter

from src.api.dependencies import UOWDep
from src.services.payments import PaymentsService
from src.schemas.payments import PaymentAddSchema

router = APIRouter(prefix="/payment")


@router.post("/deposit")
async def deposit(uow: UOWDep, data: PaymentAddSchema):
    payment = await PaymentsService().add_payment(uow, data)
    return payment


@router.delete("/refund")
async def refund(
    uow: UOWDep,
):
    pass
