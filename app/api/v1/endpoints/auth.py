from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreateResponse, UserCreate
from app.db.connection import get_db
from app.repositories.auth import AuthRepository
from app.services.auth import AuthService, EmailAlreadyExistsError


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserCreateResponse,
    response_model_exclude_defaults=True,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    repository = AuthRepository(db)
    service = AuthService(repository)

    try:
        user = await service.register_user(user_data.email, user_data.password)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return user
