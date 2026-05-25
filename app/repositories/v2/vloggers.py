from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct

from app.models.vlog import Vlog
from app.models.vlogger import Vlogger
from app.models.user import User


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
