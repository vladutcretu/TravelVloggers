from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.connection import get_db
from app.models.user import User


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user():
    pass


CurrentUser = Annotated[User, Depends(get_current_user)]
