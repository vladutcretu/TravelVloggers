from fastapi import APIRouter, status, HTTPException

from app.schemas.user import UserPublicResponse
from app.api.dependencies import DatabaseSession, CurrentUser
from app.repositories.users import UsersRepository
from app.services.users import UsersService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserPublicResponse], status_code=status.HTTP_200_OK)
async def get_users(db: DatabaseSession, current_user: CurrentUser):
    repository = UsersRepository(db)
    service = UsersService(repository)

    if current_user.is_superuser:  # request is made by a superuser
        return await service.get_users()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized"
        )
