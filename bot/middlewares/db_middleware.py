from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from utils.logger import setup_logger

# Настройка логгера
logger = setup_logger(__name__)

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool
        logger.info("DbSessionMiddleware инициализирована")

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        logger.info("Получен новый запрос, открытие сессии с базой данных")
        async with self.session_pool() as session:
            data["session"] = session
            logger.info("Сессия добавлена в контекст данных")
            try:
                from database.controller.orm_instance import orm_instance as orm

                response = await handler(event, data)
                logger.info("Запрос обработан успешно")
                return response
            except Exception as e:
                logger.error(f"Ошибка при обработке запроса: {e}")
                raise
            finally:
                logger.info("Сессия закрыта")


async def initialize_database():
    from database.controller.orm_instance import orm_instance as orm
    await orm.create_tables()
    await orm.init_demo_products()
    await orm.init_demo_exchanges()
    logger.info("Таблицы инициализированы, тарифы добавлены")