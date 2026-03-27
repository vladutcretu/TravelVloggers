from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.vlogger import Vlogger
from app.core.exceptions import VloggerAlreadyExistsError


class VloggersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vlogger(self, vlogger_data: dict[str, str]) -> Vlogger:
        new_vlogger = Vlogger(**vlogger_data)
        self.db.add(new_vlogger)

        try:
            await self.db.commit()
            await self.db.refresh(new_vlogger)
        except IntegrityError as e:
            await self.db.rollback()
            error_str = str(e.orig)
            unique_fields = [
                "youtube_channel_id",
                "youtube_channel_name",
                "youtube_channel_url",
            ]
            if any(field in error_str for field in unique_fields):
                raise VloggerAlreadyExistsError() from e
            raise e

        return new_vlogger

    async def get_vlogger_by_id(self, vlogger_id: int) -> Vlogger | None:
        result = await self.db.execute(select(Vlogger).where(Vlogger.id == vlogger_id))
        vlogger = result.scalars().first()
        return vlogger

    async def update_vlogger(self, vlogger: Vlogger) -> Vlogger:
        await self.db.commit()
        await self.db.refresh(vlogger)
        return vlogger

    async def delete_vlogger(self, vlogger: Vlogger) -> None:
        await self.db.delete(vlogger)
        await self.db.commit()
        return

    async def get_vloggers(self, skip: int, limit: int, order: str) -> list[Vlogger]:
        order_by = (
            Vlogger.created_at.asc() if order == "asc" else Vlogger.created_at.desc()
        )
        result = await self.db.execute(
            select(Vlogger).order_by(order_by).offset(skip).limit(limit)
        )
        vloggers = list(result.scalars().all())
        return vloggers
