from fastapi import APIRouter, status, HTTPException

from app.schemas.v2.vlog import (
    VlogResponse,
    VlogCreate,
    CountryData,
    VlogResponsePaginated,
)
from app.api.dependencies import CurrentUser, DatabaseSession, PaginationParams
from app.repositories.v2.vlogs import VlogsRepository
from app.services.v2.vlogs import VlogsService
from app.core.exceptions import (
    VideoIdAlreadyExistsError,
    VloggerDoesntExistError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
)


router = APIRouter(prefix="/vlogs", tags=["Vlogs"])


@router.post("", response_model=VlogResponse, status_code=status.HTTP_201_CREATED)
async def create_vlog(
    vlog_data: VlogCreate, current_user: CurrentUser, db: DatabaseSession
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    repository = VlogsRepository(db)
    service = VlogsService(repository)

    current_vlogger = await repository.get_vlogger_by_user_id(current_user.id)
    if current_vlogger is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    if vlog_data.vlogger_id != current_vlogger.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

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


@router.get(
    "/countries", response_model=list[CountryData], status_code=status.HTTP_200_OK
)
async def get_countries(db: DatabaseSession):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    countries = await service.get_countries()

    return countries


@router.get(
    "/country/{country_id}",
    response_model=VlogResponsePaginated,
    status_code=status.HTTP_200_OK,
)
async def get_vlogs_by_country(
    country_id: int,
    db: DatabaseSession,
    pagination: PaginationParams,
    language: str | None = None,
    publish_year: int | None = None,
):
    repository = VlogsRepository(db)
    service = VlogsService(repository)

    try:
        vlogs, has_more = await service.get_vlogs_by_country_id(
            country_id,
            pagination.skip,
            pagination.limit,
            pagination.order,
            language,
            publish_year,
        )
    except CountryDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country does not exist",
        )

    return {
        "vlogs": vlogs,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_more": has_more,
    }
