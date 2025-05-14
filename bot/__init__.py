from aiogram import Router
from aiogram_dialog import setup_dialogs

from bot.middlewares import db_middleware
from bot.middlewares.db_middleware import DbSessionMiddleware
from bot.middlewares.is_admin_middleware import IsAdminMiddleware
from bot.handlers.handlers import router as start_router
from bot.dialogs.start_dialog import start_dialog as start_dialog_router
from bot.dialogs.main_menu_dialog import main_menu_dialog as main_menu_dialog_router
from bot.dialogs.products_dialog import unified_store_dialog as products_dialog_router
from bot.dialogs.subscription_dialog import subscription_dialog as subscription_dialog_router
from bot.dialogs.connect_exchange_dialog import connect_exchange_dialog as connect_exchange_dialog_router
from bot.dialogs.partners_dialog import partners_dialog as partners_dialog_router
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
    router.include_router(products_dialog_router)
    router.include_router(subscription_dialog_router)
    router.include_router(connect_exchange_dialog_router)
    router.include_router(partners_dialog_router)

    setup_dialogs(router)

    return router
