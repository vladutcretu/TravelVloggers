from fastapi import APIRouter, status, HTTPException, Request

from app.schemas.v2.vlog import VlogResponsePaginated, VlogResponse, VlogYouTubeUploads
from app.schemas.v2.vlogger import VloggerPublicResponse, VloggerCountriesResponse
from app.api.dependencies import CurrentUser, DatabaseSession, PaginationParams
from app.clients.redis import YouTubeUploadsCache
from app.repositories.v2.vloggers import VloggersRepository
from app.services.v2.vloggers import VloggersService
from app.core.exceptions import (
    VloggerDoesntExistError,
    VloggerUploadsError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
    RateLimitError,
)

router = APIRouter(prefix="/vloggers", tags=["Vloggers"])


@router.get(
    "/youtube-uploads",
    response_model=VlogYouTubeUploads,
    status_code=status.HTTP_200_OK,
)
async def get_youtube_uploads(
    current_user: CurrentUser, db: DatabaseSession, request: Request
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    repository = VloggersRepository(db)
    cache = YouTubeUploadsCache(request.app.state.redis)
    service = VloggersService(repository, cache)

    try:
        youtube_uploads = await service.get_youtube_uploads(current_user.id)

    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Vlogger not found"
        )

    except VloggerUploadsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vlogger does not have uploads ID",
        )

    except YoutubeDataNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Youtube Uploads found"
        )

    return youtube_uploads


@router.post(
    "/youtube-uploads",
    response_model=VlogYouTubeUploads,
    status_code=status.HTTP_200_OK,
)
async def update_youtube_uploads(
    current_user: CurrentUser, db: DatabaseSession, request: Request
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    repository = VloggersRepository(db)
    cache = YouTubeUploadsCache(request.app.state.redis)
    service = VloggersService(repository, cache)

    try:
        youtube_uploads = await service.update_youtube_uploads(current_user.id)

    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded"
        )

    except YoutubeDataNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Youtube Uploads found"
        )

    return youtube_uploads


@router.get(
    "/{vlogger_id}",
    response_model=VloggerPublicResponse,
    status_code=status.HTTP_200_OK,
)
async def get_vlogger(vlogger_id: int, db: DatabaseSession):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        vlogger_data = await service.get_vlogger_by_id(vlogger_id)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vlogger does not exist",
        )

    return vlogger_data


@router.get(
    "/{vlogger_id}/countries",
    response_model=VloggerCountriesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_vlogger_countries(vlogger_id: int, db: DatabaseSession):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        countries = await service.get_countries_by_vlogger_id(vlogger_id)
    except VloggerDoesntExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vlogger does not exist",
        )

    return VloggerCountriesResponse(countries=countries)


@router.get(
    "/{vlogger_id}/country/{country_id}",
    response_model=VlogResponsePaginated,
    status_code=status.HTTP_200_OK,
)
async def get_vlogger_vlogs_by_country(
    vlogger_id: int,
    country_id: int,
    db: DatabaseSession,
    pagination: PaginationParams,
    language: str | None = None,
    publish_year: int | None = None,
):
    repository = VloggersRepository(db)
    service = VloggersService(repository)

    try:
        vlogs, has_more = await service.get_vlogs_by_vlogger_and_country_id(
            vlogger_id,
            country_id,
            pagination.skip,
            pagination.limit,
            pagination.order,
            language,
            publish_year,
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

    return VlogResponsePaginated(
        vlogs=[VlogResponse.model_validate(vlog) for vlog in vlogs],
        skip=pagination.skip,
        limit=pagination.limit,
        has_more=has_more,
    )
