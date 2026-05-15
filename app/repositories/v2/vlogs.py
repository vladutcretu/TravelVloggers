from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, extract
from sqlalchemy.exc import IntegrityError

from app.models.vlog import Country, Vlog
from app.models.vlogger import Vlogger
from app.core.exceptions import VideoIdAlreadyExistsError
from app.schemas.v2.vlog import CountryData


class VlogsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_vlogger_by_user_id(self, user_id: int) -> Vlogger | None:
        result = await self.db.execute(
            select(Vlogger).where(Vlogger.user_id == user_id)
        )
        vlogger = result.scalars().first()
        return vlogger

    async def get_vlog_by_youtube_id(self, youtube_video_id: str) -> Vlog | None:
        result = await self.db.execute(
            select(Vlog).where(Vlog.youtube_video_id == youtube_video_id)
        )
        vlog = result.scalars().first()
        return vlog

    async def get_vlogger_by_id(self, vlogger_id: int) -> Vlogger | None:
        result = await self.db.execute(select(Vlogger).where(Vlogger.id == vlogger_id))
        vlogger = result.scalars().first()
        return vlogger

    async def get_country_by_id(self, country_id: int) -> Country | None:
        result = await self.db.execute(select(Country).where(Country.id == country_id))
        country = result.scalars().first()
        return country

    async def create_vlog(self, new_vlog: Vlog) -> Vlog:
        self.db.add(new_vlog)
        try:
            await self.db.commit()
            await self.db.refresh(new_vlog)
        except IntegrityError as e:
            await self.db.rollback()
            error_str = str(e.orig)
            unique_fields = [
                "youtube_video_id",
            ]
            if any(field in error_str for field in unique_fields):
                raise VideoIdAlreadyExistsError() from e
            raise e

        return new_vlog

    async def get_vlog_by_id(self, vlog_id: int) -> Vlog | None:
        result = await self.db.execute(select(Vlog).where(Vlog.id == vlog_id))
        vlog = result.scalars().first()
        return vlog

    async def get_countries_with_vlog_count(self) -> list[CountryData]:
        result = await self.db.execute(
            select(
                Country.id,
                Country.name,
                Country.iso_code,
                exists().where(Vlog.country_id == Country.id).label("has_vlog"),
            )
        )

        return [
            CountryData(
                id=country.id,
                name=country.name,
                iso_code=country.iso_code,
                has_vlog=country.has_vlog,
            )
            for country in result
        ]

    async def get_vlogs_by_country_id(
        self,
        country_id: int,
        skip: int,
        limit: int,
        order: str,
        language: str | None = None,
        publish_year: int | None = None,
    ) -> list[Vlog]:
        query = select(Vlog).where(Vlog.country_id == country_id)

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
