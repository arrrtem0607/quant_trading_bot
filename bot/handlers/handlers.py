from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram_dialog import DialogManager, StartMode
from database.controller.orm_instance import orm_instance as orm
from bot.utils.statesforms import StartDialog
from bot.utils.statesforms import MainMenu
from configurations import get_config
from utils.logger import setup_logger

router = Router()
logger = setup_logger(__name__)
config = get_config()

@router.message(CommandStart())
async def start_handler(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    referrer_tg = None

    if message.text and message.text.startswith("/start ") and message.text.split(" ")[1].isdigit():
        referrer_tg = int(message.text.split(" ")[1])

    await orm.users.register_user(user_id, referrer_tg)
    user = await orm.users.get_user(user_id)

    # Если пользователь уже подтверждал условия — сразу главное меню
    if user and user.terms_accepted_at:
        await dialog_manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartDialog.language_select, mode=StartMode.RESET_STACK)

@router.message(Command("drop_tables"))
async def drop_tables_handler(message: Message):
    developer_ids = config.bot_config.get_developers_id()
    if message.from_user.id not in developer_ids:
        return await message.answer("❌ У вас нет прав на выполнение этой команды.")
    await orm.drop_tables()
    await message.answer("🗑️ Все таблицы были удалены.")

@router.message(Command("truncate_tables"))
async def truncate_tables_handler(message: Message):
    developer_ids = config.bot_config.get_developers_id()
    if message.from_user.id not in developer_ids:
        return await message.answer("❌ У вас нет прав на выполнение этой команды.")
    await orm.truncate_tables()
    await message.answer("🧹 Все таблицы были очищены.")

@router.message(Command("menu"))
async def menu_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=MainMenu.main, mode=StartMode.RESET_STACK)

@router.message(Command("language"))
async def language_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(StartDialog.language_select, mode=StartMode.RESET_STACK)


