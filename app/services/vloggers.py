from app.repositories.vloggers import VloggersRepository
from app.schemas.vlogger import VloggerCreate, VloggerUpdate
from app.models.vlogger import Vlogger


class VloggerDoesntExistError(Exception):
    pass


class VloggersService:
    def __init__(self, repository: VloggersRepository):
        self.repository = repository

    async def create_vlogger(self, vlogger_data: VloggerCreate) -> Vlogger:
        return await self.repository.create_vlogger(vlogger_data.model_dump())

    async def get_vlogger_by_id(self, vlogger_id: int) -> Vlogger:
        vlogger = await self.repository.get_vlogger_by_id(vlogger_id)
        if vlogger is None:
            raise VloggerDoesntExistError()
        return vlogger

    async def update_vlogger(
        self, vlogger: Vlogger, vlogger_data: VloggerUpdate
    ) -> Vlogger:
        updated_data = vlogger_data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(vlogger, field, value)
        return await self.repository.update_vlogger(vlogger)
