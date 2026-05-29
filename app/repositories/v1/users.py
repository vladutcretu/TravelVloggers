from datetime import datetime

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

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user

    async def update_user(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
        return

    async def update_stripe_customer_id(
        self, user: User, stripe_customer_id: str
    ) -> User:
        user.stripe_customer_id = stripe_customer_id
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_stripe_customer_id(
        self, stripe_customer_id: str
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.stripe_customer_id == stripe_customer_id)
        )
        user = result.scalars().first()
        return user

    async def update_membership(
        self, user: User, subscription_id: str, membership_expires_at: datetime
    ) -> User:
        user.stripe_subscription_id = subscription_id
        user.membership_expires_at = membership_expires_at
        await self.db.commit()
        await self.db.refresh(user)
        return user
