from sqlalchemy import select
from database.db_utils import session_manager
from database.entities.models import Product


class ProductsORM:
    def __init__(self, controller):
        self.db = controller.db

    @session_manager
    async def get_all_products(self, session) -> list[Product]:
        stmt = select(Product).where(Product.is_active.is_(True))
        result = await session.execute(stmt)
        return result.scalars().all()

    @session_manager
    async def add_product(self, session, name: str, description: str, price_usdt: float, duration_days: int):
        product = Product(
            name=name,
            description=description,
            price_usdt=price_usdt,
            duration_days=duration_days,
            is_active=True,
        )
        session.add(product)

    @session_manager
    async def get_product_by_id(self, session, product_id: int):
        stmt = select(Product).where(Product.id == product_id)
        return await session.scalar(stmt)

    @session_manager
    async def get_product(self, session, product_id: int) -> Product | None:
        return await session.scalar(
            select(Product).where(Product.id == product_id)
        )