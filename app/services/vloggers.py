from app.repositories.vloggers import VloggersRepository
from app.schemas.vlogger import VloggerCreate
from app.models.vlogger import Vlogger


class VloggerAlreadyExistsError(Exception):
    pass


class VloggersService:
    def __init__(self, repository: VloggersRepository):
        self.repository = repository

    async def create_vlogger(self, vlogger_data: VloggerCreate) -> Vlogger:
        pass
