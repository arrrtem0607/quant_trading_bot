import random

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Group, Url
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from redis.asyncio import Redis

from bot.utils.statesforms import StartDialog, MainMenu
from database.controller.orm_instance import orm_instance as orm
from bot.lexicon.lexicon_ru import LEXICON_RU

# ──────────────────────────────────────────────
# Redis и конфиг
redis = Redis(host="localhost")
MAX_ATTEMPTS = 3
BLOCK_MINUTES_RANGE = (5, 15)


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
    await orm.users.update_language(manager.event.from_user.id, lang)
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

    if data == correct:
        await dialog_manager.switch_to(StartDialog.terms)
    else:
        attempts = dialog_manager.dialog_data.get("captcha_attempts", 0) + 1
        dialog_manager.dialog_data["captcha_attempts"] = attempts

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
    await orm.users.confirm_terms(manager.event.from_user.id)
    await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)


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


# ──────────────────────────────────────────────
# Финальный диалог
start_dialog = Dialog(
    language_window,
    captcha_window,
    blocked_window,
    terms_window,
)
