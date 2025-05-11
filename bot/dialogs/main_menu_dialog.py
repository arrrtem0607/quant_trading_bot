from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Url
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery

from bot.utils.statesforms import MainMenu
from bot.lexicon.lexicon_ru import LEXICON_RU  # временно, позже заменим на автоопределение языка


async def on_stub_pressed(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.answer("⏳ Раздел в разработке", show_alert=True)


main_menu_window = Window(
    Const(LEXICON_RU["main_menu_title"]),

    Group(
        Button(Const(LEXICON_RU["menu_subs"]), id="subs", on_click=on_stub_pressed),
        Button(Const(LEXICON_RU["menu_ref"]), id="ref", on_click=on_stub_pressed),
        Url(Const(LEXICON_RU["menu_site"]), url=Const("https://quanttrading.ru")),
        Button(Const(LEXICON_RU["menu_support"]), id="support", on_click=on_stub_pressed),
        Button(Const(LEXICON_RU["menu_exchanges"]), id="exchanges", on_click=on_stub_pressed),
        width=1
    ),
    state=MainMenu.main
)

main_menu_dialog = Dialog(main_menu_window)
