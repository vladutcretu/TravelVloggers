from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vlogger import Vlogger
from app.schemas.vlogger import VloggerCreate


class VloggersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_vlogger_by_channel_id(self, channel_id) -> Vlogger | None:
        pass

    async def create_vlogger(self, vlogger_data: VloggerCreate) -> Vlogger:
        pass
