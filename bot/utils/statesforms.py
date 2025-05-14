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

class SubscriptionDialog(StatesGroup):
    show_wallet = State()
    enter_tx_hash = State()
    tx_pending = State()
    confirmed = State()

class ExchangeDialog(StatesGroup):
    choose_exchange = State()
    enter_uid = State()
    show_links = State()

class PartnersDialog(StatesGroup):
    main = State()


