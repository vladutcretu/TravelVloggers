from fastapi import APIRouter, status, HTTPException

from app.schemas.v1.user import UserPublicResponse, UserUpdate
from app.api.dependencies import CurrentUser, DatabaseSession
from app.repositories.users import UsersRepository
from app.services.users import UsersService, UserDoesntExistError


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublicResponse], status_code=status.HTTP_200_OK)
async def get_users(current_user: CurrentUser, db: DatabaseSession):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    repository = UsersRepository(db)
    service = UsersService(repository)
    return await service.get_users()


@router.patch(
    "/{user_id}", response_model=UserPublicResponse, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: int, user_data: UserUpdate, current_user: CurrentUser, db: DatabaseSession
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    repository = UsersRepository(db)
    service = UsersService(repository)

    try:
        user = await service.get_user_by_id(user_id)
    except UserDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    updated_user = await service.update_user(user, user_data)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: CurrentUser, db: DatabaseSession):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    repository = UsersRepository(db)
    service = UsersService(repository)

    try:
        user = await service.get_user_by_id(user_id)
    except UserDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    return await service.delete_user(user)
