from src.utils.unitofwork import IUnitOfWork


class OrderService:
    async def update_payment(self, uow: IUnitOfWork, order_id: int, data: OrderSchema):
        async with uow:
            order = await uow.orders.edit_one(id=order_id, data=data.model_dump())
            await uow.commit()
            return order
