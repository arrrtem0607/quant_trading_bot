import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder, Redis
from aiogram_dialog import setup_dialogs

from configurations import get_config
from bot import get_all_routers
from utils.logger import setup_logger
from bot.middlewares.db_middleware import initialize_database
from aiogram.types import BotCommand  # 🔹 добавлено
# ✅ если вы решите вынести в отдельный файл — замените на: from bot.utils.commands import setup_bot_commands

logger = setup_logger(__name__)


async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start the bot / Запустить бота"),
        BotCommand(command="/menu", description="Main menu / Главное меню"),
        BotCommand(command="/language", description="Change language / Сменить язык"),
        BotCommand(command="/drop_tables", description="⚠️ Удалить все таблицы (dev only)"),
        BotCommand(command="/truncate_tables", description="🧹 Очистить все таблицы (dev only)"),
    ]
    await bot.set_my_commands(commands)


async def run_bot():
    config = get_config()

    redis = Redis(host="localhost")
    key_builder = DefaultKeyBuilder(with_destiny=True, with_bot_id=True)
    storage = RedisStorage(redis=redis, key_builder=key_builder)

    bot = Bot(
        token=config.bot_config.get_token(),
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=storage)

    dp.include_router(await get_all_routers())
    setup_dialogs(dp)

    await setup_bot_commands(bot)  # 🔹 установка команд
    await initialize_database()
    logger.info("✅ Таблицы проверены/созданы в базе данных!")
    logger.info("✅ Бот успешно запущен")

    await dp.start_polling(bot)


async def main():
    await asyncio.gather(
        run_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
