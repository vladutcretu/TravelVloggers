from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, exists, extract

from app.models.vlog import Country, Vlog
from app.models.vlogger import Vlogger
from app.models.user import User
from app.schemas.v2.vlog import CountryData


class VloggersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_vlogger_by_user_id(self, user_id: int) -> Vlogger | None:
        result = await self.db.execute(
            select(Vlogger).where(Vlogger.user_id == user_id)
        )
        vlogger = result.scalars().first()
        return vlogger

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user

    async def get_vlogger_by_id(self, vlogger_id: int) -> Vlogger | None:
        result = await self.db.execute(select(Vlogger).where(Vlogger.id == vlogger_id))
        vlogger = result.scalars().first()
        return vlogger

    async def get_vlogs_and_countries_count_by_vlogger_id(
        self, vlogger_id: int
    ) -> tuple[int, int]:
        result_vlogs_count = await self.db.execute(
            select(func.count(Vlog.id)).where(Vlog.vlogger_id == vlogger_id)
        )
        vlogs_count = result_vlogs_count.scalar_one()

        result_countries_count = await self.db.execute(
            select(func.count(distinct(Vlog.country_id))).where(
                Vlog.vlogger_id == vlogger_id
            )
        )
        countries_count = result_countries_count.scalar_one()

        return vlogs_count, countries_count

    async def get_countries_by_vlogger_id(
        self,
        vlogger_id: int,
    ) -> list[CountryData]:
        query = select(
            Country.id,
            Country.name,
            Country.iso_code,
            exists()
            .where(Vlog.country_id == Country.id, Vlog.vlogger_id == vlogger_id)
            .label("has_vlog"),
        ).order_by(Country.name)

        result = await self.db.execute(query)
        return [
            CountryData(
                id=row.id,
                name=row.name,
                iso_code=row.iso_code,
                has_vlog=row.has_vlog,
            )
            for row in result
        ]

    async def get_country_by_id(self, country_id: int) -> Country | None:
        result = await self.db.execute(select(Country).where(Country.id == country_id))
        country = result.scalars().first()
        return country

    async def get_vlogs_by_vlogger_and_country_id(
        self,
        vlogger_id: int,
        country_id: int,
        skip: int,
        limit: int,
        order: str,
        language: str | None = None,
        publish_year: int | None = None,
    ) -> list[Vlog]:
        query = select(Vlog).where(
            Vlog.vlogger_id == vlogger_id,
            Vlog.country_id == country_id,
        )

        if language is not None:
            query = query.where(Vlog.language == language)

        if publish_year is not None:
            query = query.where(extract("year", Vlog.published_at) == publish_year)

        order_by = (
            Vlog.published_at.asc() if order == "asc" else Vlog.published_at.desc()
        )
        query = query.order_by(order_by).offset(skip).limit(limit)

        result = await self.db.execute(query)
        vlogs = list(result.scalars().all())
        return vlogs
