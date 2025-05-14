from configurations import get_config
from utils.logger import setup_logger
from sqlalchemy import select
from database.db_utils import session_manager
from database.entities.models import Transaction, User

config = get_config()
logger = setup_logger(__name__)
IS_TEST_MODE = config.payments_config.is_test_mode()

class TransactionsORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def create_transaction(
        self,
        session,
        user_id: int,
        subscription_id: int | None,
        tx_hash: str,
        amount: float
    ) -> bool:
        user_exists = await session.scalar(
            select(User.id).where(User.id == user_id)
        )
        if not user_exists:
            logger.warning("❌ Нельзя создать транзакцию: пользователь с id=%s не существует", user_id)
            return False

        # 🧪 В режиме теста последняя часть хэша может задавать сумму
        if IS_TEST_MODE and tx_hash[-3:].isdigit():
            amount = float(tx_hash[-3:])
            logger.info("🧪 Установлена тестовая сумма %s USDT из хэша %s", amount, tx_hash)

        tx = Transaction(
            user_id=user_id,
            subscription_id=subscription_id,
            tx_hash=tx_hash,
            amount_usdt=amount,
            type="payment",
            status="pending"
        )
        session.add(tx)
        return True

    @session_manager
    async def get_pending_transactions(self, session):
        result = await session.execute(
            select(Transaction).where(Transaction.status == "pending")
        )
        return result.scalars().all()

    @session_manager
    async def confirm_transaction(self, session, tx_hash: str):
        tx = await session.scalar(select(Transaction).where(Transaction.tx_hash == tx_hash))
        if tx:
            tx.status = "confirmed"
            await session.flush()
            logger.info(f"📦 Статус транзакции {tx_hash} обновлён на confirmed")

    @session_manager
    async def mark_failed(self, session, tx_hash: str) -> bool:
        tx = await session.scalar(
            select(Transaction).where(Transaction.tx_hash == tx_hash)
        )
        if tx:
            tx.status = "failed"
            await session.commit()
            return True
        return False

    @session_manager
    async def get_by_user(self, session, user_id: int) -> list[Transaction]:
        result = await session.execute(
            select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    @session_manager
    async def get_by_type(self, session, tx_type: str) -> list[Transaction]:
        result = await session.execute(
            select(Transaction).where(Transaction.type == tx_type)
        )
        return result.scalars().all()

    @session_manager
    async def get_by_status(self, session, status: str) -> list[Transaction]:
        result = await session.execute(
            select(Transaction).where(Transaction.status == status)
        )
        return result.scalars().all()
