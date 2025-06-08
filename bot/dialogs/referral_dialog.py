from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.utils.statesforms import ReferralDialog, MainMenu
from bot.lexicon.lexicon_ru import LEXICON_RU
from database.controller.orm_instance import orm_instance as orm
from utils.logger import setup_logger
from database.enums.transaction_enums import TransactionType

logger = setup_logger(__name__)

LEVEL_PERCENTS = {
    1: 35,
    2: 20,
    3: 12,
    4: 8,
    5: 4,
    6: 2.2,
    7: 1.4,
    8: 1.2,
    9: 0.6,
    10: 0.6,
}


async def referral_getter(dialog_manager, **kwargs):
    user_tg_id = dialog_manager.event.from_user.id
    user = await orm.users.get_user(user_tg_id)
    if not user:
        return {}

    tree = await orm.referrals.get_referral_tree(user.id)
    levels = []
    total = 0
    total_paid = 0
    for lvl in range(1, 11):
        ids = tree.get(lvl, [])
        count = len(ids)
        paid = await orm.referrals.count_paid(ids)
        total += count
        total_paid += paid
        levels.append({"level": lvl, "count": count, "paid": paid, "percent": LEVEL_PERCENTS[lvl]})

    earned = await orm.referrals.sum_transactions(user.id, TransactionType.REFERRAL)
    withdrawn = await orm.referrals.sum_transactions(user.id, TransactionType.WITHDRAWAL)
    balance = earned - withdrawn

    sponsor_username = None
    if user.referrer_id:
        sponsor_tg = await orm.users.get_telegram_id_by_id(user.referrer_id)
        if sponsor_tg:
            sponsor_username = f"@{sponsor_tg}"

    logger.info(f"[REFERRAL] User {user.id} requested tree. Levels: {len(tree)}")

    return {
        "levels": levels,
        "total": total,
        "paid_total": total_paid,
        "earned": earned,
        "balance": balance,
        "sponsor": sponsor_username or "-"
    }


def format_levels(data):
    lines = []
    for item in data["levels"]:
        lines.append(
            f"Уровень {item['level']} ({item['percent']}%) {item['count']}/{item['paid']} чел. Заработано ({item['paid']}) USDT"
        )
    return "\n".join(lines)


async def referral_dialog_getter(dialog_manager, **kwargs):
    data = await referral_getter(dialog_manager)
    data["levels_formatted"] = format_levels(data)
    bot = dialog_manager.middleware_data["bot"]
    bot_user = await bot.me()
    data["bot_name"] = bot_user.username
    data["user_id"] = dialog_manager.event.from_user.id
    return data


referral_window = Window(
    Format(
        "У вас есть доступ к партнерской программе!\n"
        "Партнерская программа:\n"
        "{levels_formatted}\n\n"
        "🧮 Всего партнеров: {total}\n"
        "👥 Всего партнеров, оплативших: {paid_total}\n"
        "💸 Общий заработок: {earned} USDT\n"
        "💵 Баланс: {balance} USDT (доступный баланс для вывода)\n"
        "👥 Ваш спонсор {sponsor}\n\n"
        "Копируй свою партнерскую ссылку и начинай зарабатывать!\n"
        "🔗 Ваша ссылка: t.me/{bot_name}?start={user_id}\n\n"
        "P.S: {total}/{paid_total} (зарегистрировалось/оплатило)"
    ),
    Row(
        Button(Const(LEXICON_RU["btn_back_to_menu"]), id="back_to_menu", on_click=lambda c, b, m: m.start(MainMenu.main)),
    ),
    state=ReferralDialog.main,
    getter=referral_dialog_getter
)

referral_dialog = Dialog(referral_window)
