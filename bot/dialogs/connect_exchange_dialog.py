from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select, Url, Row, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from utils.logger import setup_logger

from bot.utils.statesforms import ExchangeDialog
from bot.lexicon.lexicon_ru import LEXICON_RU
from database.controller.orm_instance import orm_instance as orm

logger = setup_logger(__name__)

# ───────────────────────────────────────────────
# Обработчики

async def on_exchange_selected(callback: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    manager.dialog_data["selected_exchange"] = item_id
    logger.info(f"[EXCHANGE] Пользователь {callback.from_user.id} выбрал биржу: {item_id}")
    await manager.switch_to(ExchangeDialog.enter_uid, show_mode=ShowMode.EDIT)


async def back_to_exchange_select(callback: CallbackQuery, button: Button, manager: DialogManager):
    logger.info(f"[BACK] Назад к выбору биржи — {callback.from_user.id}")
    await manager.switch_to(ExchangeDialog.choose_exchange, show_mode=ShowMode.EDIT)


async def back_to_uid_input(callback: CallbackQuery, button: Button, manager: DialogManager):
    logger.info(f"[BACK] Назад к вводу UID — {callback.from_user.id}")
    await manager.switch_to(ExchangeDialog.enter_uid, show_mode=ShowMode.EDIT)


async def on_uid_entered(message: Message, widget: ManagedTextInput, manager: DialogManager, uid: str):
    exchange = manager.dialog_data.get("selected_exchange")
    subscription_id = manager.start_data.get("subscription_id") or manager.dialog_data.get("subscription_id")

    if not subscription_id:
        await message.answer("❌ Не удалось сохранить UID: подписка не найдена.")
        logger.error(f"[EXCHANGE UID] Пропущен subscription_id у пользователя {message.from_user.id}")
        return

    user_id = message.from_user.id
    logger.info(f"[EXCHANGE UID] Пользователь {user_id} ввёл UID '{uid}' для {exchange}, подписка {subscription_id}")

    await orm.subscriptions.update_exchange_uid(subscription_id, exchange, uid)
    manager.dialog_data["uid"] = uid

    await manager.switch_to(ExchangeDialog.show_links, show_mode=ShowMode.DELETE_AND_SEND)


async def links_getter(dialog_manager: DialogManager, **kwargs):
    exchange_name = dialog_manager.dialog_data.get("selected_exchange")
    user_id = dialog_manager.event.from_user.id
    user = await orm.users.get_user(user_id)
    lang = user.language or "ru"

    exchange = await orm.exchanges.get_by_name(exchange_name)
    if not exchange:
        raise ValueError("Биржа не найдена в базе")

    manual_url = exchange.manual_ru if lang == "ru" else exchange.manual_en
    copy_url = exchange.copy_url_private

    logger.info(f"[EXCHANGE LINKS] Пользователь {user_id} просматривает ссылки для {exchange.name} ({lang})")

    return {
        "exchange": exchange.name,
        "manual_url": manual_url,
        "copy_url": copy_url,
    }


async def exchanges_buttons_getter(dialog_manager: DialogManager, **kwargs):
    exchanges = await orm.exchanges.get_all()
    return {"exchanges": exchanges}

# ───────────────────────────────────────────────
# Окна

select_exchange_window = Window(
    Const(LEXICON_RU["exchange_select_prompt"]),
    Select(
        text=Format("{item.name}"),
        id="exchange_selector",
        item_id_getter=lambda e: e.name,
        items="exchanges",
        on_click=on_exchange_selected,
    ),
    Row(
        Button(Const(LEXICON_RU["exchange_back_btn"]), id="back", on_click=lambda c, b, m: m.done()),
    ),
    state=ExchangeDialog.choose_exchange,
    getter=exchanges_buttons_getter
)

enter_uid_window = Window(
    Format(LEXICON_RU["exchange_enter_uid"]),
    TextInput(id="uid_input", on_success=on_uid_entered),
    Row(
        Button(Const(LEXICON_RU["exchange_back_btn"]), id="back", on_click=back_to_exchange_select),
    ),
    state=ExchangeDialog.enter_uid,
)

show_links_window = Window(
    Format(LEXICON_RU["exchange_connected_msg"]),
    Group(
        Url(Const(LEXICON_RU["exchange_manual_btn"]), url=Format("{manual_url}")),
        Url(Const(LEXICON_RU["exchange_copy_btn"]), url=Format("{copy_url}")),
        Button(Const(LEXICON_RU["exchange_register_btn"]), id="go_to_partners", on_click=lambda c, b, m: m.done()),
        width=1
    ),
    Row(
        Button(Const(LEXICON_RU["exchange_back_btn"]), id="back", on_click=back_to_uid_input),
    ),
    state=ExchangeDialog.show_links,
    getter=links_getter
)

connect_exchange_dialog = Dialog(
    select_exchange_window,
    enter_uid_window,
    show_links_window,
)
