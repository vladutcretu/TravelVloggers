from fastapi import APIRouter, status, HTTPException

from app.schemas.vlogger import VloggerCreate, VloggerResponse
from app.api.dependencies import DatabaseSession, CurrentUser
from app.repositories.vloggers import VloggersRepository
from app.services.vloggers import VloggersService, VloggerAlreadyExistsError


router = APIRouter(prefix="/vloggers", tags=["Vloggers"])


@router.post("", response_model=VloggerResponse, status_code=status.HTTP_201_CREATED)
async def create_vlogger(
    vlogger_data: VloggerCreate, db: DatabaseSession, current_user: CurrentUser
):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        vlogger = await service.create_vlogger(vlogger_data)
    except VloggerAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vlogger already exists",
        )

    return vlogger
