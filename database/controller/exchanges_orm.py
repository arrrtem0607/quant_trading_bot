from sqlalchemy import select
from database.db_utils import session_manager
from database.entities.models import Exchange


class ExchangesORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def get_all(self, session) -> list[Exchange]:
        result = await session.execute(select(Exchange).order_by(Exchange.name))
        return result.scalars().all()

    @session_manager
    async def get_by_name(self, session, name: str) -> Exchange | None:
        result = await session.execute(select(Exchange).where(Exchange.name == name))
        return result.scalar_one_or_none()

    @session_manager
    async def add_exchange(self, session, **kwargs) -> Exchange:
        exchange = Exchange(**kwargs)
        session.add(exchange)
        return exchange
