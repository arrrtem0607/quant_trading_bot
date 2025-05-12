from datetime import datetime
from sqlalchemy import select
from database.db_utils import session_manager
from database.entities.models import Subscription
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
            end_date=now,  # пока пусто — подставим позже на основании duration_days
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

