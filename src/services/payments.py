from src.schemas.payments import PaymentAddSchema
from src.utils.unitofwork import IUnitOfWork


class PaymentsService:
    async def add_payment(self, uow: IUnitOfWork, data: PaymentAddSchema):
        raw_data = data.model_dump()
        async with uow:
            payment_id = await uow.payments.add_one(raw_data)
            await uow.commit()
            return payment_id

    async def get_payment(self, uow: IUnitOfWork, payment_id: int):
        async with uow:
            user = await uow.payments.find_one(id=payment_id)
            return user
