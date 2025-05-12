import random

from aiogram import Bot
from aiogram.types import ChatMember, ChatMemberMember, ChatMemberOwner, ChatMemberAdministrator, CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Group, Url
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from redis.asyncio import Redis

from bot.utils.statesforms import StartDialog, MainMenu
from database.controller.orm_instance import orm_instance as orm
from bot.lexicon.lexicon_ru import LEXICON_RU
from utils.logger import setup_logger

# ──────────────────────────────────────────────
# Redis и конфиг
redis = Redis(host="localhost")
logger = setup_logger(__name__)
MAX_ATTEMPTS = 3
BLOCK_MINUTES_RANGE = (5, 15)
REQUIRED_CHANNEL = -1002382539061

# ──────────────────────────────────────────────
# Генерация арифметической капчи
def generate_captcha() -> tuple[str, int]:
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    if random.choice(["+", "-"]) == "+":
        return f"{a} + {b}", a + b
    else:
        return f"{a} - {b}", a - b

# ──────────────────────────────────────────────
# Выбор языка
async def on_language_selected(_: CallbackQuery, button: Button, manager: DialogManager):
    lang = "ru" if button.widget_id == "lang_ru" else "en"
    user_id = manager.event.from_user.id
    logger.info(f"[LANGUAGE] Пользователь {user_id} выбрал язык: {lang}")

    await orm.users.update_language(user_id, lang)
    user = await orm.users.get_user(user_id)

    if user and user.terms_accepted_at:
        logger.info(f"[LANGUAGE] Пользователь {user_id} уже принял условия, переход в главное меню")
        await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        logger.info(f"[LANGUAGE] Пользователь {user_id} не принял условия, переход к капче")
        await manager.switch_to(StartDialog.captcha)

language_window = Window(
    Const(LEXICON_RU["language_prompt"]),
    Row(
        Button(Const("🇷🇺 Русский"), id="lang_ru", on_click=on_language_selected),
        Button(Const("🇺🇸 English"), id="lang_en", on_click=on_language_selected),
    ),
    state=StartDialog.language_select,
)

# ──────────────────────────────────────────────
async def captcha_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    user_id = dialog_manager.event.from_user.id

    if await redis.get(f"captcha_block:{user_id}"):
        return {"captcha_expr": "🔒"}  # безопасный заглушечный текст

    # Генерация капчи при первом заходе
    if "captcha_expr" not in dialog_manager.dialog_data:
        expr, answer = generate_captcha()
        dialog_manager.dialog_data["captcha_expr"] = expr
        dialog_manager.dialog_data["captcha_answer"] = answer
        dialog_manager.dialog_data["captcha_attempts"] = 0

    return {
        "captcha_expr": dialog_manager.dialog_data["captcha_expr"]
    }

# Успешный ввод числа
async def on_captcha_success(
    message: Message,
    widget: ManagedTextInput[int],
    dialog_manager: DialogManager,
    data: int,
) -> None:
    user_id = message.from_user.id
    correct = dialog_manager.dialog_data.get("captcha_answer")
    logger.info(f"[CAPTCHA] Пользователь {user_id} ввёл {data}, правильный ответ: {correct}")


    if data == correct:
        logger.info(f"[CAPTCHA] Пользователь {user_id} успешно прошёл капчу")
        await dialog_manager.switch_to(StartDialog.terms)
    else:
        attempts = dialog_manager.dialog_data.get("captcha_attempts", 0) + 1
        dialog_manager.dialog_data["captcha_attempts"] = attempts
        logger.warning(f"[CAPTCHA] Неправильный ввод. Попытка {attempts}/{MAX_ATTEMPTS}")

        if attempts >= MAX_ATTEMPTS:
            minutes = random.randint(*BLOCK_MINUTES_RANGE)
            await redis.set(f"captcha_block:{user_id}", "1", ex=minutes * 60)
            await message.answer(LEXICON_RU["captcha_failed"].format(minutes=minutes))
            await dialog_manager.switch_to(StartDialog.blocked)
        else:
            await message.answer(LEXICON_RU["captcha_wrong"].format(tries_left=MAX_ATTEMPTS - attempts))


# Ошибка: не число
async def on_captcha_error(
    message: Message,
    widget: ManagedTextInput[int],
    dialog_manager: DialogManager,
    error: ValueError,
) -> None:
    await message.answer("❌ Введите число, пожалуйста.")

captcha_window = Window(
    Format(LEXICON_RU["captcha_question"], when="captcha_expr"),
    TextInput(
        id="captcha_input",
        type_factory=int,
        on_success=on_captcha_success,
        on_error=on_captcha_error,
    ),
    state=StartDialog.captcha,
    getter=captcha_getter,
)

# ──────────────────────────────────────────────
# Принятие условий
async def on_terms_accepted(_: CallbackQuery, __: Button, manager: DialogManager):
    user_id = manager.event.from_user.id
    await orm.users.confirm_terms(user_id)
    logger.info(f"[TERMS] Пользователь {user_id} принял условия. Переход к проверке подписки.")
    await manager.switch_to(StartDialog.subscription_check)

terms_window = Window(
    Const(LEXICON_RU["terms_text"]),
    Group(
        Url(Const(LEXICON_RU["terms_read_btn"]), url=Const(LEXICON_RU["terms_url"])),
        Button(Const(LEXICON_RU["terms_accept"]), id="accept", on_click=on_terms_accepted),
        width=1
    ),
    state=StartDialog.terms,
)

async def blocked_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    user_id = dialog_manager.event.from_user.id
    ttl = await redis.ttl(f"captcha_block:{user_id}")
    return {"ttl": max(ttl, 0)}

async def on_retry(_: CallbackQuery, __: Button, manager: DialogManager):
    user_id = manager.event.from_user.id
    ttl = await redis.ttl(f"captcha_block:{user_id}")
    if ttl <= 0:
        await manager.switch_to(StartDialog.captcha)
    else:
        await manager.switch_to(StartDialog.blocked)

blocked_window = Window(
    Format("⏳ Вы временно заблокированы.\n"
           "Осталось: <b>{ttl}</b> сек.\n\n"
           "Нажмите кнопку ниже, чтобы попробовать снова."),
    Button(Const("🔁 Проверить повторно"), id="retry", on_click=on_retry),
    state=StartDialog.blocked,
    getter=blocked_getter,
)

async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        member: ChatMember = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        #logger.info(f"[SUBSCRIPTION][API] Ответ get_chat_member для {user_id} в {REQUIRED_CHANNEL}: {member}")
        return isinstance(member, (ChatMemberMember, ChatMemberOwner, ChatMemberAdministrator))
    except Exception as e:
        #logger.warning(f"[SUBSCRIPTION][ERROR] Ошибка при проверке подписки пользователя {user_id}: {e}")
        return False

async def subscription_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    bot = dialog_manager.middleware_data["bot"]

    is_subscribed = await check_subscription(user_id, bot)
    return {"is_subscribed": is_subscribed}

async def on_check_subscription(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = callback.from_user.id
    bot = manager.middleware_data["bot"]
    logger.info(f"[SUBSCRIPTION] Пользователь {user_id} нажал 'Проверить подписку'")

    subscribed = await check_subscription(user_id, bot)
    if subscribed:
        logger.info(f"[SUBSCRIPTION] Пользователь {user_id} подписан — переход в главное меню")
        await callback.answer("✅ Подписка подтверждена", show_alert=True)
        await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        logger.warning(f"[SUBSCRIPTION] Пользователь {user_id} не подписан")
        await callback.answer("❌ Вы ещё не подписались", show_alert=True)

async def on_continue_after_subscription(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = callback.from_user.id
    bot = manager.middleware_data["bot"]
    logger.info(f"[SUBSCRIPTION] Пользователь {user_id} нажал 'ДАЛЕЕ'")

    if await check_subscription(user_id, bot):
        logger.info(f"[SUBSCRIPTION] Пользователь {user_id} подписан. Переход в главное меню.")
        await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
    else:
        logger.warning(f"[SUBSCRIPTION] Пользователь {user_id} не подписан. Блокируем переход.")
        await callback.answer("❌ Подпишитесь на канал для продолжения", show_alert=True)

subscription_window = Window(
    Const("📢 Подпишитесь на канал, чтобы продолжить:"),
    Group(
        Url(Const("📲 Перейти в канал"), url=Const("https://t.me/+spOjqukB9iI1NzRi")),
        Button(Const("🔁 Проверить подписку"), id="check_sub", on_click=on_check_subscription),
        width=1
    ),
    state=StartDialog.subscription_check,
)

# ──────────────────────────────────────────────
# Финальный диалог
start_dialog = Dialog(
    language_window,
    captcha_window,
    blocked_window,
    terms_window,
    subscription_window,  # 👈 добавлено
)
