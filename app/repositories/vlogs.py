from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from app.models.vlog import Country, Vlog
from app.models.vlogger import Vlogger
from app.core.exceptions import VideoIdAlreadyExistsError


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

    async def update_vlog(self, vlog: Vlog) -> Vlog:
        await self.db.commit()
        await self.db.refresh(vlog)
        return vlog

    async def delete_vlog(self, vlog: Vlog) -> None:
        await self.db.delete(vlog)
        await self.db.commit()
        return

    async def get_vlogs(self, skip: int, limit: int, order: str) -> list[Vlog]:
        order_by = Vlog.created_at.asc() if order == "asc" else Vlog.created_at.desc()

        result = await self.db.execute(
            select(Vlog).order_by(order_by).offset(skip).limit(limit)
        )
        vlogs = list(result.scalars().all())
        return vlogs
