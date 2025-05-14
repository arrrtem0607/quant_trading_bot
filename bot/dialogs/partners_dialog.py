from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Url, Row, Button, ListGroup
from aiogram_dialog.widgets.text import Const, Format
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.utils.statesforms import PartnersDialog, MainMenu
from database.controller.orm_instance import orm_instance as orm
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def partners_getter(dialog_manager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    exchanges = await orm.exchanges.get_all()
    filtered = [e for e in exchanges if e.referral_url]

    logger.info(f"[PARTNERS] Пользователь {user_id} открыл окно партнёров. Найдено: {len(filtered)} ссылок.")
    return {"exchanges": [{"id": e.id, "name": e.name, "url": e.referral_url} for e in filtered]}


partners_window = Window(
    Const(LEXICON_RU["partners_title"]),
    ListGroup(
        Url(
            Format("🌐 {item[name]}"),
            Format("{item[url]}"),
            id="exchange_link",
        ),
        id="partners_list",
        item_id_getter=lambda item: item["id"],
        items="exchanges",
    ),
    Row(
        Button(
            Const(LEXICON_RU["btn_back_to_menu"]),
            id="back_to_menu",
            on_click=lambda c, b, m: m.start(MainMenu.main)
        ),
    ),
    state=PartnersDialog.main,
    getter=partners_getter,
)

partners_dialog = Dialog(partners_window)
