from aiogram_dialog import Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, Group, Url
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery

from bot.utils.statesforms import MainMenu, UnifiedStore, PartnersDialog
from bot.lexicon.lexicon_ru import LEXICON_RU

# ──────────────────────────────────────────────
# HANDLERS

async def on_products_pressed(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(UnifiedStore.showcase, show_mode=ShowMode.EDIT)

async def on_my_subs_pressed(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(UnifiedStore.dashboard, show_mode=ShowMode.EDIT)

async def on_stub_pressed(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(PartnersDialog.main, show_mode=ShowMode.EDIT)

# ──────────────────────────────────────────────
# WINDOW

main_menu_window = Window(
    Const(LEXICON_RU["main_menu_title"]),
    Group(
        Button(Const("📄 Мои подписки"), id="my_subs", on_click=on_my_subs_pressed),
        Button(Const(LEXICON_RU["menu_subs"]), id="subs", on_click=on_products_pressed),
        Button(Const(LEXICON_RU["menu_ref"]), id="ref", on_click=on_stub_pressed),
        Url(Const(LEXICON_RU["menu_site"]), url=Const("https://quanttrading.ru")),
        Button(Const(LEXICON_RU["menu_support"]), id="support", on_click=on_stub_pressed),
        Button(Const(LEXICON_RU["menu_exchanges"]), id="exchanges", on_click=on_stub_pressed),
        width=1
    ),
    state=MainMenu.main
)

main_menu_dialog = Dialog(main_menu_window)
