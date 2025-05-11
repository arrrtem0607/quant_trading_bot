from aiogram.fsm.state import StatesGroup, State


class StartDialog(StatesGroup):
    language_select = State()
    captcha = State()
    terms = State()
    blocked = State()


class MainMenu(StatesGroup):
    main = State()
