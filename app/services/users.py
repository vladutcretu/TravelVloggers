from app.repositories.users import UsersRepository
from app.models.user import User
from app.schemas.user import UserUpdate


class UserDoesntExistError(Exception):
    pass


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def get_users(self) -> list[User]:
        return await self.repository.get_users()

    async def get_user_by_id(self, user_id) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if user is None:
            raise UserDoesntExistError()
        return user

    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        updated_data = user_data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(user, field, value)
        return await self.repository.update_user(user)

    async def delete_user(self, user: User) -> None:
        return await self.repository.delete_user(user)
