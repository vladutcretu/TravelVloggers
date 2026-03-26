from app.repositories.vlogs import VlogsRepository
from app.models.vlog import Country


class VlogsService:
    def __init__(self, repository: VlogsRepository):
        self.repository = repository

    async def get_countries(
        self, skip: int, limit: int, order: str, search: str | None
    ) -> tuple[list[Country], bool]:
        countries = await self.repository.get_countries(skip, limit + 1, order, search)
        has_more = len(countries) > limit
        countries = countries[:limit]
        return countries, has_more
