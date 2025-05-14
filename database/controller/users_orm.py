from datetime import datetime
from sqlalchemy import select
from database.db_utils import session_manager
from database.entities.models import User


class UsersORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def register_user(self, session, telegram_id: int, referrer_id: int | None = None):
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            return {"message": "Пользователь уже зарегистрирован"}

        new_user = User(telegram_id=telegram_id, referrer_id=referrer_id)
        session.add(new_user)
        return {"message": "Пользователь зарегистрирован"}

    @session_manager
    async def get_user(self, session, telegram_id: int) -> User | None:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))

    @session_manager
    async def update_language(self, session, telegram_id: int, language: str) -> bool:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            user.language = language
            return True
        return False

    @session_manager
    async def confirm_terms(self, session, telegram_id: int) -> bool:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user:
            user.terms_accepted_at = datetime.utcnow().replace(tzinfo=None)  # <-- FIX
            return True
        return False

    @session_manager
    async def get_id_by_telegram(self, session, telegram_id: int) -> int | None:
        result = await session.execute(select(User.id).where(User.telegram_id == telegram_id))
        return result.scalar()

    @session_manager
    async def get_telegram_id_by_id(self, session, user_id: int) -> int | None:
        stmt = select(User.telegram_id).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()



