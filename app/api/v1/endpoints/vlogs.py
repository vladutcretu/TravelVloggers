from fastapi import APIRouter, status, Query

from app.schemas.vlog import CountryResponsePaginated, CountryResponse
from app.api.dependencies import DatabaseSession, PaginationParams
from app.repositories.vlogs import VlogsRepository
from app.services.vlogs import VlogsService


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
