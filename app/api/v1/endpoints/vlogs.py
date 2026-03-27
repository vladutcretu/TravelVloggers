from fastapi import APIRouter, status, Query, HTTPException

from app.schemas.vlog import (
    CountryResponsePaginated,
    CountryResponse,
    VlogResponse,
    VlogCreate,
)
from app.api.dependencies import DatabaseSession, PaginationParams, CurrentUser
from app.repositories.vlogs import VlogsRepository
from app.services.vlogs import (
    VlogsService,
    VideoIdAlreadyExistsError,
    VloggerDoesntExistError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
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
    service = VlogsService(repository)

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
