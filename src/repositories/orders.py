from src.models.models import Order
from src.utils.repository import SQLAlchemyRepository


class OrdersRepository(SQLAlchemyRepository):
    model = Order
