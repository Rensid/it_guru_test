from src.models.models import Payment
from src.utils.repository import SQLAlchemyRepository


class PaymentsRepository(SQLAlchemyRepository):
    model = Payment
