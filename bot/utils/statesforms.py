from aiogram.fsm.state import StatesGroup, State


class StartDialog(StatesGroup):
    language_select = State()
    captcha = State()
    blocked = State()
    terms = State()
    subscription_check = State()  # 👈 добавили


class MainMenu(StatesGroup):
    main = State()


class UnifiedStore(StatesGroup):
    dashboard = State()        # окно с активными подписками
    showcase = State()         # окно со списком всех продуктов
    product_detail = State()   # (позже) окно с детальной информацией о продукте
    payment = State()          # (позже) окно оплаты
    exchange_select = State()  # (позже) выбор биржи


