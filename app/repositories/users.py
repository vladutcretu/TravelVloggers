from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class UsersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        return list(users)
