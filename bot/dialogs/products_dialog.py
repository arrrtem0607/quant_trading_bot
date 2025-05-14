from datetime import datetime

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select
from magic_filter import F

from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.utils.statesforms import UnifiedStore, SubscriptionDialog, ExchangeDialog
from database.controller.orm_instance import orm_instance as orm
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ───────────────────────────────────────────────
# HANDLERS
async def on_back_to_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    logger.info(f"[BACK] Пользователь {callback.from_user.id} возвращается в главное меню")
    from bot.utils.statesforms import MainMenu
    await manager.start(MainMenu.main, show_mode=ShowMode.EDIT)

async def to_showcase(callback: CallbackQuery, button: Button, manager: DialogManager):
    logger.info(f"[NAVIGATION] Пользователь {callback.from_user.id} переходит в витрину")
    await manager.switch_to(UnifiedStore.showcase, ShowMode.EDIT)

async def to_dashboard(callback: CallbackQuery, button: Button, manager: DialogManager):
    logger.info(f"[NAVIGATION] Пользователь {callback.from_user.id} переходит в дашборд")
    await manager.switch_to(UnifiedStore.dashboard, ShowMode.EDIT)

async def on_product_selected(callback: CallbackQuery, widget: Select, manager: DialogManager, item_id: int):
    logger.info(f"[SELECT] Пользователь {callback.from_user.id} выбрал продукт {item_id}")
    manager.dialog_data["selected_product_id"] = int(item_id)
    await manager.switch_to(UnifiedStore.product_detail, ShowMode.EDIT)

async def on_pay_subscription(callback: CallbackQuery, button: Button, manager: DialogManager):
    selected_product_id = manager.dialog_data.get("selected_product_id")
    if selected_product_id is None:
        logger.error("[ERROR] selected_product_id отсутствует в dialog_data")
        raise ValueError("selected_product_id отсутствует в dialog_data")

    user_id = await orm.users.get_id_by_telegram(callback.from_user.id)
    logger.info(f"[PAY] Пользователь {user_id} оформляет подписку на продукт {selected_product_id}")
    subscription = await orm.subscriptions.create_draft(user_id=user_id, product_id=selected_product_id)

    logger.info(f"[PAY] Черновик подписки создан: ID={subscription.id}")
    await manager.start(
        SubscriptionDialog.show_wallet,
        data={
            "product_id": selected_product_id,
            "subscription_id": subscription.id
        },
        show_mode=ShowMode.EDIT
    )

async def on_connect_exchange(callback: CallbackQuery, button: Button, manager: DialogManager):
    subscription_id = manager.dialog_data.get("subscription_id")
    if not subscription_id:
        logger.warning(f"[EXCHANGE] Нет subscription_id в dialog_data для пользователя {callback.from_user.id}")
        await callback.answer("❌ Не удалось определить подписку", show_alert=True)
        return

    logger.info(f"[EXCHANGE] Пользователь {callback.from_user.id} подключает биржу для подписки {subscription_id}")
    await manager.start(
        ExchangeDialog.choose_exchange,
        data={"subscription_id": subscription_id},
        show_mode=ShowMode.EDIT
    )

# ───────────────────────────────────────────────
# GETTERS
async def subscriptions_getter(dialog_manager: DialogManager, **kwargs):
    user_id = await orm.users.get_id_by_telegram(dialog_manager.event.from_user.id)
    now = datetime.utcnow()

    subs = await orm.subscriptions.get_user_active_subscriptions(user_id)
    logger.info(f"[MY SUBS] Пользователь {user_id} — активных подписок: {len(subs)}")

    if not subs:
        logger.info(f"[MY SUBS] У пользователя {user_id} нет активных подписок")
        return {
            "subs_text": LEXICON_RU["subs_no_active"],
            "has_subs": False
        }

    blocks = []
    for sub in subs:
        product = await orm.products.get_product_by_id(sub.product_id)
        left_days = (sub.end_date - now).days if sub.end_date else None

        logger.info(f"[MY SUBS] Подписка на {product.name}: осталось {left_days} дней")

        block = (
            f"🔹 <b>{product.name}</b>\n"
            f"{product.description}\n"
            f"{LEXICON_RU['subs_until'].format(end_date=sub.end_date.date())}"
        )

        if left_days is not None and left_days <= 30:
            block += f"\n{LEXICON_RU['subs_recommend_renew']}"

        blocks.append(block)

    return {
        "subs_text": "\n\n".join(blocks),
        "has_subs": True
    }

async def showcase_getter(dialog_manager: DialogManager, **kwargs):
    products = await orm.products.get_all_products()
    logger.info(f"[SHOWCASE] Загружено {len(products)} продуктов для отображения")

    showcase_text = "\n".join(
        f"🔹 <b>{p.name}</b> — {p.price_usdt} USDT / {p.duration_days} дней"
        for p in products
    )

    return {
        "products": products,
        "showcase_text": showcase_text
    }

async def product_detail_getter(dialog_manager: DialogManager, **kwargs):
    product_id = int(dialog_manager.dialog_data.get("selected_product_id"))
    user_id = await orm.users.get_id_by_telegram(dialog_manager.event.from_user.id)

    product = await orm.products.get_product_by_id(product_id)
    dialog_manager.dialog_data["product_id"] = product.id

    active_sub = await orm.subscriptions.get_user_active_subscription_for_product(
        user_id=user_id,
        product_id=product_id
    )

    if active_sub:
        dialog_manager.dialog_data["subscription_id"] = active_sub.id
        logger.info(f"[DETAIL] У пользователя {user_id} есть активная подписка ID={active_sub.id} на продукт {product_id}")
    else:
        logger.info(f"[DETAIL] У пользователя {user_id} НЕТ активной подписки на продукт {product_id}")

    left_days = None
    if active_sub and active_sub.end_date:
        left_days = (active_sub.end_date - datetime.utcnow()).days

    return {
        "product": product,
        "sub": active_sub,
        "has_sub": bool(active_sub),
        "left_days": left_days
    }

# ───────────────────────────────────────────────
# WINDOWS
subscriptions_window = Window(
    Format(LEXICON_RU["subs_title"] + "\n{subs_text}"),
    Button(Const(LEXICON_RU["btn_renew"]), id="extend", on_click=to_showcase, when="has_subs"),
    Button(
        Const(LEXICON_RU["btn_open_store"]),
        id="go_to_store",
        on_click=to_showcase,
        when=~F["has_subs"]
    ),
    Button(Const(LEXICON_RU["btn_back_to_menu"]), id="back", on_click=on_back_to_menu),
    state=UnifiedStore.dashboard,
    getter=subscriptions_getter,
)

showcase_window = Window(
    Format(LEXICON_RU["store_title"] + "\n{showcase_text}"),
    ScrollingGroup(
        Select(
            Format(LEXICON_RU["store_product_button"]),
            id="product_selector",
            item_id_getter=lambda x: x.id,
            items="products",
            on_click=on_product_selected,
        ),
        id="products_scroll",
        width=1,
        height=8,
    ),
    Button(Const(LEXICON_RU["btn_back_to_menu"]), id="back", on_click=on_back_to_menu),
    state=UnifiedStore.showcase,
    getter=showcase_getter,
)

product_detail_window = Window(
    Format(LEXICON_RU["product_detail_text"]),
    Button(Const(LEXICON_RU["btn_subscribe"]), id="pay", on_click=on_pay_subscription, when=~F["has_sub"]),
    Button(Const(LEXICON_RU["btn_renew_sub"]), id="renew", on_click=on_pay_subscription, when=F["has_sub"]),
    Button(Const(LEXICON_RU["btn_connect_exchange"]), id="connect", on_click=on_connect_exchange, when="has_sub"),
    Button(Const(LEXICON_RU["btn_back_to_store"]), id="back_to_store", on_click=to_showcase),
    state=UnifiedStore.product_detail,
    getter=product_detail_getter
)


# ───────────────────────────────────────────────
# DIALOG (Единый)
unified_store_dialog = Dialog(
    subscriptions_window,
    showcase_window,
    product_detail_window
)
