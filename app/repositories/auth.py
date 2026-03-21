from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        return existing_user

    async def create_user(
        self, email: str, hashed_password: str, is_superuser: bool = False
    ):
        new_user = User(
            email=email, password_hash=hashed_password, is_superuser=is_superuser
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
