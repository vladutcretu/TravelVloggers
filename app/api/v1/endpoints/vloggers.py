from fastapi import APIRouter, status, HTTPException

from app.schemas.vlogger import (
    VloggerResponse,
    VloggerCreate,
    VloggerUpdate,
    VloggerResponsePaginated,
)
from app.api.dependencies import CurrentUser, DatabaseSession, PaginationParams
from app.repositories.vloggers import VloggersRepository, VloggerAlreadyExistsError
from app.services.vloggers import VloggersService, VloggerDoesntExistError


router = APIRouter(prefix="/vloggers", tags=["Vloggers"])


@router.post("", response_model=VloggerResponse, status_code=status.HTTP_201_CREATED)
async def create_vlogger(
    vlogger_data: VloggerCreate, current_user: CurrentUser, db: DatabaseSession
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
            status_code=status.HTTP_409_CONFLICT, detail="Vlogger already exists"
        )

    return vlogger


@router.patch(
    "/{vlogger_id}", response_model=VloggerResponse, status_code=status.HTTP_200_OK
)
async def update_vlogger(
    vlogger_id: int,
    vlogger_data: VloggerUpdate,
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
        vlogger = await service.get_vlogger_by_id(vlogger_id)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlogger does not exist"
        )

    updated_vlogger = await service.update_vlogger(vlogger, vlogger_data)
    return updated_vlogger


@router.delete("/{vlogger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vlogger(
    vlogger_id: int, current_user: CurrentUser, db: DatabaseSession
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        vlogger = await service.get_vlogger_by_id(vlogger_id)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlogger does not exist"
        )

    return await service.delete_vlogger(vlogger)


@router.get("", response_model=VloggerResponsePaginated, status_code=status.HTTP_200_OK)
async def get_vloggers(db: DatabaseSession, pagination: PaginationParams):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    vloggers, has_more = await service.get_vloggers(
        pagination.skip, pagination.limit, pagination.order
    )

    return VloggerResponsePaginated(
        vloggers=[VloggerResponse.model_validate(vlogger) for vlogger in vloggers],
        skip=pagination.skip,
        limit=pagination.limit,
        has_more=has_more,
    )


@router.get(
    "/{vlogger_id}", response_model=VloggerResponse, status_code=status.HTTP_200_OK
)
async def get_vlogger(vlogger_id: int, db: DatabaseSession):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        vlogger = await service.get_vlogger_by_id(vlogger_id)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlogger does not exist"
        )

    return vlogger
