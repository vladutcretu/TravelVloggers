from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
