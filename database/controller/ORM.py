from sqlalchemy import inspect, text, select

from database.entities.core import Base, Database
from database.controller.users_orm import UsersORM
from database.controller.products_orm import ProductsORM
from database.controller.subscriptions_orm import SubscriptionsORM
from database.controller.transactions_orm import TransactionsORM
from database.controller.exchanges_orm import ExchangesORM
from database.controller.referrals_orm import ReferralsORM
from database.db_utils import session_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ORMController:
    def __init__(self, db: Database = Database()):
        self.db = db
        self.users = UsersORM(self)
        self.products = ProductsORM(self)
        self.subscriptions = SubscriptionsORM(self)
        self.transactions = TransactionsORM(self)
        self.exchanges = ExchangesORM(self)
        self.referrals = ReferralsORM(self)
        logger.info("ORMController initialized")

    async def create_tables(self):
        async with self.db.async_engine.begin() as conn:

            def sync_inspect(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()

            logger.info(f"🔍 Используемая база данных: {self.db.async_engine.url.database}")

            await conn.run_sync(lambda c: c.execute(text("SET search_path TO public")))

            existing_tables = await conn.run_sync(sync_inspect)
            logger.info(f"📌 Существующие таблицы: {existing_tables}")

            found_metadata_tables = [
                name.split(".")[-1]  # убираем 'public.' из 'public.users'
                for name in Base.metadata.tables.keys()
            ]
            logger.info(f"📂 Найденные таблицы в metadata: {found_metadata_tables}")

            if existing_tables and set(existing_tables) != set(found_metadata_tables):
                logger.warning("⚠️ Обнаружены изменения в моделях! Пересоздаем таблицы...")

                await conn.run_sync(Base.metadata.drop_all)
                logger.info("🗑️ Все таблицы удалены!")

                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Таблицы успешно пересозданы!")

            elif not existing_tables:
                logger.info("🔧 Таблицы отсутствуют, создаем их...")
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Таблицы успешно созданы!")
            else:
                logger.info("✅ Структура БД актуальна, изменений не требуется.")

    async def drop_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(lambda c: c.execute(text("SET search_path TO public")))
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("🗑️ Все таблицы удалены вручную!")

    async def truncate_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(lambda c: c.execute(text("SET search_path TO public")))
            tables = Base.metadata.sorted_tables
            for table in tables:
                await conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
            logger.info("🧹 Все таблицы очищены (TRUNCATE).")

    @session_manager
    async def init_demo_products(self, session):
        from database.entities.models import Product

        existing = await session.execute(select(Product))
        if existing.scalars().first():
            return  # уже есть

        products = [
            Product(
                name="Закрытый Копи Трейдинг",
                description="🤖 Автоматизированная торговля с копированием сделок алготрейдеров.",
                price_usdt=250.0,
                duration_days=365,
                is_active=True
            ),
            Product(
                name="⚠️ Высоко-рискованный сигнальный бот",
                description="🔥 Сигналы для агрессивной ручной торговли. Идеально для опытных трейдеров.",
                price_usdt=300.0,
                duration_days=100,
                is_active=False
            ),
            Product(
                name="🧠 Бот крипто ОПЦИОНОВ",
                description="Скоро будет доступно",
                price_usdt=350.0,
                duration_days=150,
                is_active=False
            ),
            Product(
                name="⚡️ Майнинг БУУУУСТ",
                description="Подать заявку на ускорение майнинга через наш сервис.",
                price_usdt=400.0,
                duration_days=200,
                is_active=True
            ),
            Product(
                name="🧩 Индивидуальная стратегия",
                description="Персональный подход к трейдингу. Заполните заявку.",
                price_usdt=1.0,
                duration_days=1,
                is_active=True
            ),
            Product(
                name="🔒 Секретная разработка",
                description="Скоро будет доступно.",
                price_usdt=14.0,
                duration_days=1,
                is_active=False
            ),
            Product(
                name="⚙️ Помощь с размещением оборудования",
                description="Подать заявку для сопровождения в подключении/размещении майнинга.",
                price_usdt=35.0,
                duration_days=1,
                is_active=True
            ),
            Product(
                name="💻 Купить майнинг оборудование",
                description="Проконсультируем и поможем приобрести оборудование. Подайте заявку.",
                price_usdt=100000.0,
                duration_days=365,
                is_active=True
            ),
        ]

        session.add_all(products)

    @session_manager
    async def init_demo_exchanges(self, session):
        from database.entities.models import Exchange

        existing = await session.execute(select(Exchange))
        if existing.scalars().first():
            return  # уже есть биржи

        exchanges = [
            Exchange(
                name="Bybit",
                manual_ru="https://telegra.ph/Instrukciya-po-podklyucheniyu-k-torgovomu-algoritmu-04-26-3",
                manual_en="https://telegra.ph/Instructions-for-connecting-to-the-trading-algorithm-04-27-4",
                copy_url_private="https://i.bybit.com/1K2SVab4?action=inviteToCopy",
                referral_url="https://www.bybit.com/invite?ref=51RK2X",
                referral_code="51RK2X"
            ),
            Exchange(
                name="BingX",
                manual_ru="https://telegra.ph/Instrukciya-po-podklyucheniyu-k-torgovomu-algoritmu-04-21",
                manual_en="https://telegra.ph/Instructions-for-connecting-to-the-trading-algorithm-04-27-3",
                copy_url_private="https://general.bingx.com/4Apbwl",
                referral_url="https://bingx.com/partner/TradingBRO/",
                referral_code="TradingBRO"
            ),
            Exchange(
                name="Blofin",
                manual_ru="https://telegra.ph/Instrukciya-po-podklyucheniyu-k-torgovomu-algoritmu-04-26-2",
                manual_en="https://telegra.ph/Instructions-for-connecting-to-the-trading-algorithm-04-27",
                copy_url_private="https://general.bingx.com/2WmLfi",
                referral_url="https://blofin.com/register?referral_code=tc8JY7",
                referral_code="tc8JY7"
            ),
            Exchange(
                name="OKX",
                manual_ru="https://telegra.ph/Instrukciya-po-podklyucheniyu-k-torgovomu-algoritmu-04-26",
                manual_en="https://telegra.ph/Instructions-for-connecting-to-the-trading-algorithm-04-27-5",
                copy_url_private="https://okx.com/ul/F0j4Cbr",
                referral_url="https://www.okx.com/join/13149794",
                referral_code="13149794"
            ),
            Exchange(
                name="Bitget",
                manual_ru="https://telegra.ph/Instrukciya-po-podklyucheniyu-k-torgovomu-algoritmu-04-25",
                manual_en="https://telegra.ph/Instructions-for-connecting-to-the-trading-algorithm-04-27-2",
                copy_url_private="https://www.bitget.com/ru/copy-trading/trader/beb1497687bb3e53a390/futures?vipCode=e4ba&inviteCode=b9b34a728db73d51a390940767",
                referral_url="https://partner.bitget.com/bg/TSQ3LM",
                referral_code="TSQ3LM"
            )
        ]

        session.add_all(exchanges)



