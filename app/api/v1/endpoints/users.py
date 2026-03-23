from fastapi import APIRouter, status, HTTPException

from app.schemas.user import UserPublicResponse, UserUpdate
from app.api.dependencies import DatabaseSession, CurrentUser
from app.repositories.users import UsersRepository
from app.services.users import UsersService, UserDoesntExistError


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublicResponse], status_code=status.HTTP_200_OK)
async def get_users(db: DatabaseSession, current_user: CurrentUser):
    repository = UsersRepository(db)
    service = UsersService(repository)

    if current_user.is_superuser:  # request is made by a superuser
        return await service.get_users()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.patch(
    "/{user_id}", response_model=UserPublicResponse, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: int, user_data: UserUpdate, db: DatabaseSession, current_user: CurrentUser
):
    repository = UsersRepository(db)
    service = UsersService(repository)

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await service.get_user_by_id(user_id)
    except UserDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    updated_user = await service.update_user(user, user_data)
    return updated_user
