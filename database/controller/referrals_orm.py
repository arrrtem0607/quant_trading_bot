from datetime import datetime
from sqlalchemy import select, func

from database.db_utils import session_manager
from database.entities.models import User, Subscription, Transaction, Referral
from database.enums.subscription_enums import SubscriptionStatus
from database.enums.transaction_enums import TransactionType, TransactionStatus


class ReferralsORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def get_referral_tree(self, session, user_id: int, max_level: int = 10) -> dict[int, list[int]]:
        tree: dict[int, list[int]] = {}
        current_ids = [user_id]
        for level in range(1, max_level + 1):
            if not current_ids:
                break
            stmt = select(User.id).where(User.referrer_id.in_(current_ids))
            result = await session.execute(stmt)
            ids = result.scalars().all()
            tree[level] = ids
            current_ids = ids
        return tree

    @session_manager
    async def count_paid(self, session, user_ids: list[int]) -> int:
        if not user_ids:
            return 0
        stmt = select(func.count(func.distinct(Subscription.user_id))).where(
            Subscription.user_id.in_(user_ids),
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.end_date >= datetime.utcnow()
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    @session_manager
    async def sum_transactions(self, session, user_id: int, tx_type: TransactionType) -> float:
        stmt = select(func.coalesce(func.sum(Transaction.amount_usdt), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == tx_type,
            Transaction.status == TransactionStatus.CONFIRMED
        )
        result = await session.execute(stmt)
        return float(result.scalar() or 0)
    @session_manager
    async def get_levels_stats(self, session, user_id: int, max_level: int = 10) -> dict[int, dict]:
        stats: dict[int, dict] = {}
        current_ids = [user_id]
        for level in range(1, max_level + 1):
            if not current_ids:
                break
            users_stmt = select(User.id).where(User.referrer_id.in_(current_ids))
            ids = (await session.execute(users_stmt)).scalars().all()

            if ids:
                count = len(ids)
                paid_stmt = select(func.count(func.distinct(Subscription.user_id))).where(
                    Subscription.user_id.in_(ids),
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.end_date >= datetime.utcnow(),
                )
                paid = (await session.execute(paid_stmt)).scalar() or 0
            else:
                count = 0
                paid = 0

            earned_stmt = select(func.coalesce(func.sum(Referral.reward_usdt), 0)).where(
                Referral.referrer_id == user_id,
                Referral.level == level,
            )
            earned = (await session.execute(earned_stmt)).scalar() or 0

            stats[level] = {"count": count, "paid": paid, "earned": float(earned)}
            current_ids = ids

        return stats

    @session_manager
    async def sum_rewards(self, session, referrer_id: int, level: int | None = None) -> float:
        stmt = select(func.coalesce(func.sum(Referral.reward_usdt), 0)).where(
            Referral.referrer_id == referrer_id
        )
        if level is not None:
            stmt = stmt.where(Referral.level == level)
        result = await session.execute(stmt)
        return float(result.scalar() or 0)
