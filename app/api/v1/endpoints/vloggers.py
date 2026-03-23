from fastapi import APIRouter, status, HTTPException

from app.schemas.vlogger import VloggerResponse, VloggerCreate
from app.api.dependencies import CurrentUser, DatabaseSession
from app.repositories.vloggers import VloggersRepository, VloggerAlreadyExistsError
from app.services.vloggers import VloggersService


router = APIRouter(prefix="/vloggers", tags=["Vloggers"])


@router.post("", response_model=VloggerResponse, status_code=status.HTTP_201_CREATED)
async def create_vlogger(
    vlogger_data: VloggerCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        vlogger = await service.create_vlogger(vlogger_data)
    except VloggerAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Vlogger already exists"
        )

    return vlogger
