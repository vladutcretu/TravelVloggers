from fastapi import APIRouter, status, Query, HTTPException

from app.schemas.v1.vlog import (
    CountryResponsePaginated,
    CountryResponse,
    VlogResponse,
    VlogCreate,
    VlogUpdate,
    VlogResponsePaginated,
    CountryVlogsResponsePaginated,
)
from app.api.dependencies import DatabaseSession, PaginationParams, CurrentUser
from app.repositories.vlogs import VlogsRepository
from app.services.vlogs import VlogsService
from app.clients.youtube import YoutubeClient
from app.core.exceptions import (
    VideoIdAlreadyExistsError,
    VloggerDoesntExistError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
    VlogDoesntExistError,
)


router = APIRouter(prefix="/vlogs", tags=["Vlogs"])


@router.get(
    "/countries",
    response_model=CountryResponsePaginated,
    status_code=status.HTTP_200_OK,
)
async def get_countries(
    db: DatabaseSession,
    pagination: PaginationParams,
    search: str | None = Query(None, max_length=50),
):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    countries, has_more = await service.get_countries(
        pagination.skip, pagination.limit, pagination.order, search
    )

    return CountryResponsePaginated(
        countries=[CountryResponse.model_validate(country) for country in countries],
        skip=pagination.skip,
        limit=pagination.limit,
        has_more=has_more,
    )


@router.post("", response_model=VlogResponse, status_code=status.HTTP_201_CREATED)
async def create_vlog(
    vlog_data: VlogCreate, current_user: CurrentUser, db: DatabaseSession
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    repository = VlogsRepository(db)
    youtube_client = YoutubeClient()
    service = VlogsService(repository, youtube_client)

    try:
        vlog = await service.create_vlog(vlog_data)
    except VideoIdAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Youtube Video ID already exists",
        )
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vlogger does not exist",
        )
    except CountryDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country does not exist",
        )
    except YoutubeDataNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Youtube Data not found",
        )

    return vlog


@router.patch("/{vlog_id}", response_model=VlogResponse, status_code=status.HTTP_200_OK)
async def update_vlog(
    vlog_id: int, vlog_data: VlogUpdate, current_user: CurrentUser, db: DatabaseSession
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    repository = VlogsRepository(db)
    service = VlogsService(repository)

    try:
        vlog = await service.get_vlog_by_id(vlog_id)
    except VlogDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlog does not exist"
        )

    try:
        updated_vlog = await service.update_vlog(vlog, vlog_data)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vlogger does not exist",
        )
    except CountryDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country does not exist",
        )

    return updated_vlog


@router.delete("/{vlog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vlog(vlog_id: int, current_user: CurrentUser, db: DatabaseSession):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    repository = VlogsRepository(db)
    service = VlogsService(repository)

    try:
        vlog = await service.get_vlog_by_id(vlog_id)
    except VlogDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlog does not exist"
        )

    return await service.delete_vlog(vlog)


@router.get("", response_model=VlogResponsePaginated, status_code=status.HTTP_200_OK)
async def get_vlogs(db: DatabaseSession, pagination: PaginationParams):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    vlogs, has_more = await service.get_vlogs(
        pagination.skip, pagination.limit, pagination.order
    )

    return VlogResponsePaginated(
        vlogs=[VlogResponse.model_validate(vlog) for vlog in vlogs],
        skip=pagination.skip,
        limit=pagination.limit,
        has_more=has_more,
    )


@router.get("/{vlog_id}", response_model=VlogResponse, status_code=status.HTTP_200_OK)
async def get_vlog(vlog_id: int, db: DatabaseSession):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    try:
        vlog = await service.get_vlog_by_id(vlog_id)
    except VlogDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vlog does not exist"
        )

    return vlog


@router.get(
    "/country/{country_id}",
    response_model=CountryVlogsResponsePaginated,
    status_code=status.HTTP_200_OK,
)
async def get_vlogs_by_country(
    country_id: int, db: DatabaseSession, pagination: PaginationParams
):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    try:
        country, vlogs, has_more = await service.get_vlogs_by_country_id(
            country_id, pagination.skip, pagination.limit, pagination.order
        )
    except CountryDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country does not exist"
        )

    return CountryVlogsResponsePaginated(
        id=country.id,
        name=country.name,
        iso_code=country.iso_code,
        vlogs=[VlogResponse.model_validate(vlog) for vlog in vlogs],
        skip=pagination.skip,
        limit=pagination.limit,
        has_more=has_more,
    )
