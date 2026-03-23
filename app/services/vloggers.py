from app.repositories.vloggers import VloggersRepository
from app.schemas.vlogger import VloggerCreate
from app.models.vlogger import Vlogger


class VloggersService:
    def __init__(self, repository: VloggersRepository):
        self.repository = repository

    async def create_vlogger(self, vlogger_data: VloggerCreate) -> Vlogger:
        return await self.repository.create_vlogger(vlogger_data.model_dump())
