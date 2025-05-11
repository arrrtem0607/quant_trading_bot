from sqlalchemy import (
    BigInteger, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP,
    Numeric, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from database.entities.core import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=True)
    terms_accepted_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    referrals = relationship(
        "Referral",
        back_populates="referrer",
        cascade="all, delete",
        foreign_keys="[Referral.referrer_id]",
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price_usdt: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.products.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    end_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="inactive")
    exchange: Mapped[str] = mapped_column(String(100), nullable=True)
    exchange_uid: Mapped[str] = mapped_column(String(100), nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    subscription_id: Mapped[int] = mapped_column(Integer, ForeignKey("public.subscriptions.id"), nullable=True)
    tx_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    amount_usdt: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_usdt: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    referrer = relationship(
        "User",
        back_populates="referrals",
        foreign_keys=[referrer_id],
    )


class Log(Base):
    __tablename__ = "logs"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("public.users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
