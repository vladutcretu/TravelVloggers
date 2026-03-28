from app.repositories.vlogs import VlogsRepository
from app.models.vlog import Country, Vlog
from app.schemas.vlog import VlogCreate, VlogUpdate
from app.clients.youtube import YoutubeClient
from app.core.exceptions import (
    VideoIdAlreadyExistsError,
    VloggerDoesntExistError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
    VlogDoesntExistError,
)


class VlogsService:
    def __init__(
        self, repository: VlogsRepository, youtube_client: YoutubeClient | None = None
    ):
        self.repository = repository
        self.youtube_client = youtube_client

    async def get_countries(
        self, skip: int, limit: int, order: str, search: str | None
    ) -> tuple[list[Country], bool]:
        countries = await self.repository.get_countries(skip, limit + 1, order, search)
        has_more = len(countries) > limit
        countries = countries[:limit]
        return countries, has_more

    async def create_vlog(self, vlog_data: VlogCreate) -> Vlog:
        # 1. check duplicate and validate data
        existing_vlog = await self.repository.get_vlog_by_youtube_id(
            vlog_data.youtube_video_id
        )
        if existing_vlog:
            raise VideoIdAlreadyExistsError()

        existing_vlogger = await self.repository.get_vlogger_by_id(vlog_data.vlogger_id)
        if existing_vlogger is None:
            raise VloggerDoesntExistError()

        existing_country = await self.repository.get_country_by_id(vlog_data.country_id)
        if existing_country is None:
            raise CountryDoesntExistError()

        # 2. call Youtube API
        if self.youtube_client is None:
            raise RuntimeError("YoutubeClient must be provided to create_vlog endpoint")
        youtube_data = await self.youtube_client.get_video_data(
            vlog_data.youtube_video_id
        )
        if youtube_data is None:
            raise YoutubeDataNotFoundError()

        # 3. map data
        new_vlog = Vlog(
            vlogger_id=vlog_data.vlogger_id,
            country_id=vlog_data.country_id,
            youtube_video_id=vlog_data.youtube_video_id,
            published_at=youtube_data.published_at,
            title=youtube_data.title,
            thumbnail_url=youtube_data.thumbnail_url,
            language=youtube_data.language,
        )

        # 4. create object
        return await self.repository.create_vlog(new_vlog)

    async def get_vlog_by_id(self, vlog_id: int) -> Vlog:
        vlog = await self.repository.get_vlog_by_id(vlog_id)
        if vlog is None:
            raise VlogDoesntExistError()
        return vlog

    async def update_vlog(self, vlog: Vlog, vlog_data: VlogUpdate) -> Vlog:
        updated_data = vlog_data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(vlog, field, value)
        return await self.repository.update_vlog(vlog)
