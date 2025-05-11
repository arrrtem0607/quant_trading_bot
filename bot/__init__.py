from aiogram import Router
from aiogram_dialog import setup_dialogs

from bot.middlewares.db_middleware import DbSessionMiddleware
from bot.middlewares.is_admin_middleware import IsAdminMiddleware
from bot.handlers.handlers import router as start_router
from bot.dialogs.start_dialog import start_dialog as start_dialog_router
from bot.dialogs.main_menu_dialog import main_menu_dialog as main_menu_dialog_router
from database.entities.core import Database
from configurations import get_config

config = get_config()

async def get_all_routers():
    # Создаем экземпляры миддлваров
    db: Database = Database()
    db_session_middleware = DbSessionMiddleware(db.async_session_factory)


    # Подключаем миддлвары к start_router (обычные функции)
    start_router.message.middleware(db_session_middleware)
    start_router.callback_query.middleware(db_session_middleware)

    router: Router = Router()

    router.include_router(start_router)
    router.include_router(start_dialog_router)
    router.include_router(main_menu_dialog_router)

    setup_dialogs(router)

    return router
