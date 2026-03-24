from sqlalchemy import func, select
from src.models.models import Payment
from src.utils.repository import SQLAlchemyRepository


class PaymentsRepository(SQLAlchemyRepository):
    model = Payment

    async def get_sum(self, order_id: int):
        stmt = select(func.sum(self.model.amount)).where(
            self.model.order_id == order_id
        )
        amounts_sum = await self.session.execute(stmt)
        return amounts_sum.scalar()
