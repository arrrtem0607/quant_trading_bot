from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_utils import session_manager
from database.entities.models import Subscription, Product
from database.enums.subscription_enums import SubscriptionStatus


class SubscriptionsORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def get_user_active_subscriptions(self, session, user_id: int) -> list[Subscription]:
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.end_date >= datetime.utcnow()
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @session_manager
    async def add_subscription(self, session, user_id: int, product_id: int, exchange: str = None, exchange_uid: str = None):
        now = datetime.utcnow()
        sub = Subscription(
            user_id=user_id,
            product_id=product_id,
            start_date=now,
            end_date=now,  # заменится при активации
            status=SubscriptionStatus.INACTIVE,
            exchange=exchange,
            exchange_uid=exchange_uid
        )
        session.add(sub)
        return sub

    @session_manager
    async def get_user_active_subscription_for_product(self, session, user_id: int, product_id: int):
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.product_id == product_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.end_date >= datetime.utcnow()
        ).limit(1)
        return await session.scalar(stmt)

    @session_manager
    async def create_draft(self, session: AsyncSession, user_id: int, product_id: int) -> Subscription:
        new_sub = Subscription(
            user_id=user_id,
            product_id=product_id,
            status=SubscriptionStatus.PENDING,
            start_date=None,
            end_date=None
        )
        session.add(new_sub)
        await session.flush()  # для получения ID
        return new_sub

    @session_manager
    async def activate_subscription(self, session: AsyncSession, subscription_id: int):
        subscription = await session.get(Subscription, subscription_id)
        if not subscription:
            return

        # Получим duration_days из product
        stmt = select(Product.duration_days).where(Product.id == subscription.product_id)
        result = await session.execute(stmt)
        duration_days = result.scalar_one_or_none()

        if duration_days is None:
            return  # продукт не найден

        now = datetime.utcnow()
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.start_date = now
        subscription.end_date = now + timedelta(days=duration_days)
