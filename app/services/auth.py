from sqlalchemy.exc import IntegrityError

from app.repositories.auth import AuthRepository
from app.core.security import hash_password
from app.core.config import settings


class EmailAlreadyExistsError(Exception):
    pass


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register_user(self, email: str, password: str):
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
