from app.repositories.users import UsersRepository
from app.models.user import User


class UsersService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def get_users(self) -> list[User]:
        return await self.repository.get_users()
