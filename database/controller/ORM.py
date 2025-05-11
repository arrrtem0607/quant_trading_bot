from sqlalchemy import inspect, text

from database.entities.core import Base, Database
from database.controller.users_orm import UsersORM
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ORMController:
    def __init__(self, db: Database = Database()):
        self.db = db
        self.users = UsersORM(self)
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

