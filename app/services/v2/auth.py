from datetime import timedelta

from fastapi import HTTPException, status

from app.repositories.v2.auth import AuthRepository
from app.models.user import User
from app.models.vlogger import Vlogger
from app.core.security import decode_google_token, create_access_token
from app.core.exceptions import (
    UserDoesntExistError,
    GoogleIdAlreadyExistsError,
    EmailAlreadyExistsError,
    YoutubeDataNotFoundError,
    GoogleInvalidTokenError,
    GoogleIncompleteTokenError,
)
from app.clients.youtube import YoutubeClient
from app.core.config import settings


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def login_with_google(
        self, google_id_token: str
    ) -> tuple[User, Vlogger | None]:
        try:
            user_data = decode_google_token(google_id_token)
        except (GoogleInvalidTokenError, GoogleIncompleteTokenError) as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        user = await self.repository.login_with_google(user_data.google_id)
        if not user:
            raise UserDoesntExistError()

        vlogger = await self.repository.get_vlogger_by_user_id(user.id)

        return user, vlogger

    async def register_with_google(
        self, google_id_token: str, access_token: str
    ) -> tuple[User, Vlogger]:
        try:
            user_data = decode_google_token(google_id_token)
        except (GoogleInvalidTokenError, GoogleIncompleteTokenError) as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        
        # Validate data
        existing_user = await self.repository.get_user_by_google_id(user_data.google_id)
        if existing_user:
            raise GoogleIdAlreadyExistsError()

        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise EmailAlreadyExistsError()

        # Fetch YouTube API for Vlogger data
        try:
            youtube_client = YoutubeClient()
            channel_data = await youtube_client.get_channel_data(access_token)
            uploads_id = await youtube_client.get_uploads_id(channel_data.youtube_channel_id)
        except YoutubeDataNotFoundError:
            raise YoutubeDataNotFoundError()

        # Create User and Vlogger
        user = await self.repository.register_with_google(
            user_data.google_id, user_data.email, user_data.full_name
        )

        # Check if Vlogger exists by unique fields
        existing_vlogger = await self.repository.get_vlogger_by_any_unique_fields(
            youtube_channel_id=channel_data.youtube_channel_id,
            youtube_channel_name=channel_data.youtube_channel_name,
            youtube_channel_url=channel_data.youtube_channel_url,
        )

        if existing_vlogger:
            if existing_vlogger.user_id is None:
                vlogger = await self.repository.update_vlogger(
                    vlogger_id=existing_vlogger.id, user_id=user.id
                )
            else:
                vlogger = existing_vlogger

        vlogger = await self.repository.create_vlogger(
            user_id=user.id,
            youtube_channel_id=channel_data.youtube_channel_id,
            youtube_channel_name=channel_data.youtube_channel_name,
            youtube_channel_url=channel_data.youtube_channel_url,
            youtube_avatar_url=channel_data.youtube_avatar_url,
            youtube_subscribers_count=channel_data.youtube_subscribers_count,
            youtube_uploads_id=str(uploads_id),
        )

        return user, vlogger

    async def create_access_token(self, user_id: int) -> str:
        access_token_expires_in = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires_in
        )
        return access_token
