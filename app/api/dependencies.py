from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.db.connection import get_db
from app.repositories.auth import AuthRepository
from app.services.auth import (
    AuthService,
    AccessTokenInvalidError,
    UserDoesntExistError,
)


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DatabaseSession,
) -> User:
    repository = AuthRepository(db)
    service = AuthService(repository)

    token = credentials.credentials

    try:
        user_id = await service.get_user_by_token(token)
    except AccessTokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await service.get_user_by_id(user_id)
    except UserDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
