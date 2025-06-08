from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Url
from aiogram_dialog.widgets.text import Const, Format

from bot.utils.statesforms import SupportDialog, MainMenu
from bot.lexicon.lexicon_ru import LEXICON_RU
from configurations import get_config

config = get_config()


async def support_getter(dialog_manager, **kwargs):
    return {"support_link": config.bot_config.get_support_link()}


support_window = Window(
    Format(LEXICON_RU["support_message"]),
    Row(
        Url(Const(LEXICON_RU["support_open"]), url=Format("@arrrteminc")),
        Button(Const(LEXICON_RU["btn_back_to_menu"]), id="back_to_menu", on_click=lambda c, b, m: m.start(MainMenu.main)),
    ),
    state=SupportDialog.main,
    getter=support_getter,
)

support_dialog = Dialog(support_window)
