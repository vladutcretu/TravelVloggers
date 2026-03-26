from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.vlog import Country


class VlogsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_countries(
        self, skip: int, limit: int, order: str, search: str | None
    ) -> list[Country]:
        query = select(Country)
        if search:
            query = query.where(
                or_(
                    Country.name.ilike(f"%{search}%"),
                    Country.iso_code.like(f"%{search.upper()}%"),
                )
            )

        order_by = Country.name.asc() if order == "asc" else Country.name.desc()
        result = await self.db.execute(
            query.order_by(order_by).offset(skip).limit(limit)
        )
        countries = list(result.scalars().all())
        return countries
