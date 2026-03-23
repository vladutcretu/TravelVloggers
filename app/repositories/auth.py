from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.user import User


class EmailAlreadyExistsError(Exception):
    pass


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        return existing_user

    async def create_user(
        self, email: str, hashed_password: str, is_superuser: bool = False
    ) -> User:
        new_user = User(
            email=email, password_hash=hashed_password, is_superuser=is_superuser
        )
        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except IntegrityError:
            await self.db.rollback()
            raise EmailAlreadyExistsError()

        return new_user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user
