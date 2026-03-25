from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException, status
from src.schemas.orders import OrderPaymentStatus
from src.schemas.payments import PaymentAddSchema, PaymentStatus
from src.utils.http_client import BaseHttpClient, HttpUoW
from src.utils.unitofwork import IUnitOfWork


class BasePaymentService(ABC):
    @abstractmethod
    async def deposite(
        self,
        uow: IUnitOfWork,
        data: PaymentAddSchema,
        http_uow: Optional[HttpUoW] = None,
    ): ...

    @abstractmethod
    async def refund(
        self, uow: IUnitOfWork, payment_id: int, http_uow: Optional[HttpUoW] = None
    ): ...


class CashPaymentService(BasePaymentService):
    async def deposite(self, uow: IUnitOfWork, data: PaymentAddSchema, **kwargs):
        raw_data = data.model_dump()
        async with uow:
            order = await uow.orders.find_one(id=data.order_id)

            if order.payment_status == OrderPaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order is already fully paid",
                )

            if data.amount > order.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment cannot exceed order amount",
                )

            await uow.payments.add_one(raw_data)

            if data.amount == order.amount:
                new_status = OrderPaymentStatus.PAID
            else:
                new_status = OrderPaymentStatus.PARTIALLY_PAID

            await uow.orders.edit_one(order.id, {"payment_status": new_status})
            await uow.commit()

    async def refund(self, uow: IUnitOfWork, payment_id: int, **kwargs):
        async with uow:
            payment = await uow.payments.find_one(id=payment_id)

            if not payment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment not found",
                )
            if payment.status == PaymentStatus.REFUNDED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment already refunded",
                )

            await uow.payments.edit_one(payment.id, {"status": PaymentStatus.REFUNDED})

            order = await uow.orders.find_one(id=payment.order_id)

            payments_sum = await uow.payments.get_sum(payment.order_id)

            if payments_sum == 0:
                new_status = OrderPaymentStatus.NOT_PAID
            elif payments_sum < order.amount:
                new_status = OrderPaymentStatus.PARTIALLY_PAID
            else:
                new_status = OrderPaymentStatus.PAID

            await uow.orders.edit_one(order.id, {"payment_status": new_status})

            await uow.commit()

            return {"status": "refunded"}


class AcquiringService(BasePaymentService):
    async def deposite(
        self, uow: IUnitOfWork, data: PaymentAddSchema, http_uow: HttpUoW
    ):
        async with uow:
            order = await uow.orders.find_one(id=data.order_id)

            if order.payment_status == OrderPaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order already paid",
                )

            async with http_uow:
                bank_payment_id = await http_uow.bank.acquiring_start(
                    order.id, data.amount
                )

            payment = await uow.payments.add_one(
                {
                    **data.model_dump(),
                    "status": PaymentStatus.PENDING,
                    "bank_payment_id": bank_payment_id,
                }
            )
            await uow.commit()
            return {
                "payment_id": payment.id,
                "bank_payment_id": bank_payment_id,
            }

    async def refund(
        self,
        uow: IUnitOfWork,
        payment_id: int,
        http_uow: Optional[HttpUoW] = None,
    ):
        if http_uow is None:
            raise ValueError("http_uow is required for AcquiringService")

        async with uow:
            payment = await uow.payments.find_one(id=payment_id)

            if not payment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment not found",
                )

            if payment.status != PaymentStatus.SUCCESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only successful payments can be refunded",
                )

            async with http_uow:
                bank_data = await http_uow.bank.acquiring_check(payment.bank_payment_id)

            bank_status = bank_data.get("status")

            if bank_status != "refunded":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment is not refunded in bank system",
                )

            await uow.payments.update_one(
                {"id": payment_id},
                {"status": PaymentStatus.REFUNDED},
            )

            await uow.commit()

            return {
                "payment_id": payment.id,
                "status": PaymentStatus.REFUNDED,
            }
