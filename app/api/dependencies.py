from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.user import User
from app.db.connection import get_db
from app.core.config import settings
from app.repositories.auth import AuthRepository
from app.services.auth import (
    AuthService,
    AccessTokenInvalidError,
    UserDoesntExistError,
)


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


# CurrentUser dependency logic
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


# PaginationParams dependency logic
class Pagination(BaseModel):
    skip: int
    limit: int
    order: str


def pagination_params(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.responses_per_page,
    order: Annotated[Literal["asc", "desc"], Query()] = "asc",
) -> Pagination:
    return Pagination(skip=skip, limit=limit, order=order)


PaginationParams = Annotated[Pagination, Depends(pagination_params)]
