from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram.types import Message, CallbackQuery

from bot.utils.statesforms import SubscriptionDialog, UnifiedStore
from database.controller.orm_instance import orm_instance as orm
from bot.lexicon.lexicon_ru import LEXICON_RU
from configurations import get_config

config = get_config()

WALLET_ADDRESS = config.payments_config.get_wallet_address()

async def back_to_showcase(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(UnifiedStore.showcase, show_mode=ShowMode.EDIT)

async def wallet_getter(dialog_manager: DialogManager, **kwargs):
    product_id = dialog_manager.start_data.get("product_id")
    subscription_id = dialog_manager.start_data.get("subscription_id")

    if product_id is None:
        raise ValueError("product_id отсутствует в start_data")

    # ✅ Сохраняем в dialog_data
    dialog_manager.dialog_data["subscription_id"] = subscription_id

    product = await orm.products.get_product_by_id(product_id)

    return {
        "product_name": product.name if product else "Неизвестный продукт",
        "amount_usdt": product.price_usdt if product else 0,
        "wallet_address": WALLET_ADDRESS,
        "product_id": product_id,
        "subscription_id": subscription_id,
    }

wallet_window = Window(
    Format(LEXICON_RU["subs_wallet_prompt"]),
    Button(Const(LEXICON_RU["subs_paid_btn"]), id="paid", on_click=lambda c, b, m: m.switch_to(SubscriptionDialog.enter_tx_hash)),
    Button(Const(LEXICON_RU["subs_back_btn"]), id="back_to_store", on_click=back_to_showcase),
    state=SubscriptionDialog.show_wallet,
    getter=wallet_getter,
)

async def back_to_show_wallet(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(SubscriptionDialog.show_wallet, show_mode=ShowMode.EDIT)

async def on_tx_hash_entered(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    tx_hash: str,
):
    if not tx_hash.startswith("0x") or len(tx_hash) < 66 or not tx_hash[-3:].isdigit():
        await message.answer(LEXICON_RU["subs_tx_invalid"])
        return

    telegram_id = message.from_user.id
    user_id = await orm.users.get_id_by_telegram(telegram_id)

    if not user_id:
        await message.answer(LEXICON_RU["subs_user_not_found"])
        return

    subscription_id = dialog_manager.dialog_data.get("subscription_id")
    amount_usdt = int(tx_hash[-3:])

    await orm.transactions.create_transaction(
        user_id=user_id,
        subscription_id=subscription_id,
        tx_hash=tx_hash,
        amount=amount_usdt
    )

    await message.answer(LEXICON_RU["subs_tx_saved"])
    await dialog_manager.start(
        UnifiedStore.dashboard,
        data={"subscription_id": subscription_id},
        show_mode=ShowMode.DELETE_AND_SEND
    )

hash_input_window = Window(
    Const(LEXICON_RU["subs_tx_prompt"]),
    TextInput(id="tx_hash_input", on_success=on_tx_hash_entered),
    Button(Const(LEXICON_RU["subs_back_btn"]), id="back_to_store", on_click=back_to_show_wallet),
    state=SubscriptionDialog.enter_tx_hash,
)

subscription_dialog = Dialog(
    wallet_window,
    hash_input_window,
)
