from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import async_session_factory
from src.repositories.orders import OrdersRepository
from src.repositories.payments import PaymentsRepository


class IUnitOfWork(ABC):
    session: AsyncSession
    orders: OrdersRepository
    payments: PaymentsRepository

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.orders = OrdersRepository(self.session)
        self.payments = PaymentsRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
