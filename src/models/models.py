from typing import List

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.db import Base
from src.schemas.orders import OrderPaymentStatus
from src.schemas.payments import PaymentStatus, PaymentType


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "payment_status IN ('not_paid', 'partially_paid', 'paid')",
            name="check_order_payment_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    payment_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=OrderPaymentStatus.NOT_PAID,
        server_default=text("'not_paid'"),
    )

    payments: Mapped[List["Payment"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'success', 'failed', 'refunded')",
            name="check_order_payment_status",
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType, native_enum=False), nullable=False
    )

    status: Mapped[PaymentStatus] = mapped_column(
        String,
        default=PaymentStatus.PENDING,
        nullable=True,
    )

    bank_payment_id: Mapped[str | None] = mapped_column(String, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="payments")
