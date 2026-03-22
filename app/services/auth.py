from datetime import timedelta

from sqlalchemy.exc import IntegrityError

from app.repositories.auth import AuthRepository
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from app.core.config import settings


class EmailAlreadyExistsError(Exception):
    pass


class EmailOrPasswordIncorrectError(Exception):
    pass


class AccessTokenInvalidError(Exception):
    pass


class UserDoesntExistsError(Exception):
    pass


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register_user(self, email: str, password: str) -> User:
        email = email.lower()

        existing_user = await self.repository.get_user_by_email(email)
        if existing_user:
            raise EmailAlreadyExistsError()

        hashed_password = hash_password(password)

        is_superuser = email == settings.SUPERUSER_EMAIL

        try:
            user = await self.repository.create_user(
                email, hashed_password, is_superuser
            )
        except IntegrityError:
            raise EmailAlreadyExistsError()
        return user

    async def login_user(self, email: str, password: str) -> str:
        email = email.lower()

        existing_user = await self.repository.get_user_by_email(email)
        if existing_user is None:
            raise EmailOrPasswordIncorrectError()

        verified_password = verify_password(password, existing_user.password_hash)
        if verified_password is False:
            raise EmailOrPasswordIncorrectError()

        access_token_expires_in = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data={"sub": str(existing_user.id)}, expires_delta=access_token_expires_in
        )
        return access_token

    async def get_user_by_token(self, token: str) -> int:
        user_id = verify_access_token(token)
        if user_id is None:
            raise AccessTokenInvalidError()
        return user_id

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise UserDoesntExistsError()
        return user
