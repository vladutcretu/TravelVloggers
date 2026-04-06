from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.vlogger import Vlogger
from app.core.exceptions import (
    UserAlreadyExistsError,
    VloggerDoesntExistError,
    VloggerAlreadyExistsError,
)


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login_with_google(self, google_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        existing_user = result.scalars().first()
        return existing_user

    async def get_vlogger_by_user_id(self, user_id: int) -> Vlogger | None:
        result = await self.db.execute(
            select(Vlogger).where(Vlogger.user_id == user_id)
        )
        existing_vlogger = result.scalars().first()
        return existing_vlogger

    async def get_user_by_google_id(self, google_id: str) -> User | None:
        return await self.login_with_google(google_id)

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        return existing_user

    async def register_with_google(
        self, google_id: str, email: str, full_name: str
    ) -> User:
        new_user = User(email=email, google_id=google_id, full_name=full_name)
        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except IntegrityError as e:
            await self.db.rollback()
            raise UserAlreadyExistsError() from e

        return new_user

    async def get_vlogger_by_any_unique_fields(
        self,
        youtube_channel_id: str,
        youtube_channel_name: str,
        youtube_channel_url: str,
    ) -> Vlogger | None:
        result = await self.db.execute(
            select(Vlogger).where(
                or_(
                    Vlogger.youtube_channel_id == youtube_channel_id,
                    Vlogger.youtube_channel_name == youtube_channel_name,
                    Vlogger.youtube_channel_url == youtube_channel_url,
                )
            )
        )
        existing_vlogger = result.scalars().first()
        return existing_vlogger

    async def update_vlogger(
        self,
        vlogger_id: int,
        user_id: int | None = None,
        youtube_channel_name: str | None = None,
        youtube_avatar_url: str | None = None,
        youtube_subscribers_count: int | None = None,
        youtube_uploads_id: str | None = None,
    ) -> Vlogger:
        result = await self.db.execute(select(Vlogger).where(Vlogger.id == vlogger_id))
        vlogger = result.scalars().first()
        if not vlogger:
            raise VloggerDoesntExistError()

        if user_id is not None:
            vlogger.user_id = user_id
        if youtube_channel_name is not None:
            vlogger.youtube_channel_name = youtube_channel_name
        if youtube_avatar_url is not None:
            vlogger.youtube_avatar_url = youtube_avatar_url
        if youtube_subscribers_count is not None:
            vlogger.youtube_subscribers_count = youtube_subscribers_count
        if youtube_uploads_id is not None:
            vlogger.youtube_uploads_id = youtube_uploads_id

        self.db.add(vlogger)
        await self.db.commit()
        await self.db.refresh(vlogger)

        return vlogger

    async def create_vlogger(
        self,
        user_id: int,
        youtube_channel_id: str,
        youtube_channel_name: str,
        youtube_channel_url: str,
        youtube_avatar_url: str,
        youtube_subscribers_count: int,
        youtube_uploads_id: str,
    ) -> Vlogger:
        new_vlogger = Vlogger(
            user_id=user_id,
            youtube_channel_id=youtube_channel_id,
            youtube_channel_name=youtube_channel_name,
            youtube_channel_url=youtube_channel_url,
            youtube_avatar_url=youtube_avatar_url,
            youtube_subscribers_count=youtube_subscribers_count,
            youtube_uploads_id=youtube_uploads_id,
        )

        self.db.add(new_vlogger)
        try:
            await self.db.commit()
            await self.db.refresh(new_vlogger)
        except IntegrityError as e:
            await self.db.rollback()
            raise VloggerAlreadyExistsError() from e

        return new_vlogger
