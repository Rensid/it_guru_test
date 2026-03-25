from src.schemas.payments import PaymentStatus
from src.utils.http_client import HttpUoW
from src.utils.unitofwork import UnitOfWork


async def check_status():
    async with UnitOfWork() as uow:
        payments = await uow.payments.find_all_with_filter(status=PaymentStatus.PENDING)

        if not payments:
            return

        async with HttpUoW() as http_uow:
            for payment in payments:
                data = await http_uow.bank.acquiring_check(payment.id)
                new_status_str = data.get("status")

                if new_status_str != PaymentStatus.PENDING:
                    new_status = PaymentStatus(new_status_str)
                    await uow.payments.edit_one(payment.id, {"status": new_status})
