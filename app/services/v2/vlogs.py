from app.repositories.v2.vlogs import VlogsRepository
from app.schemas.v2.vlog import VlogCreate, CountryData
from app.models.vlog import Vlog
from app.clients.youtube import YoutubeClient
from app.core.exceptions import (
    VideoIdAlreadyExistsError,
    VloggerDoesntExistError,
    CountryDoesntExistError,
    YoutubeDataNotFoundError,
    VlogDoesntExistError,
)


class VlogsService:
    def __init__(self, repository: VlogsRepository):
        self.repository = repository

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
        youtube_client = YoutubeClient()
        youtube_data = await youtube_client.get_video_data(vlog_data.youtube_video_id)
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

    async def get_countries(self) -> list[CountryData]:
        return await self.repository.get_countries_with_vlog_count()

    async def get_vlogs_by_country_id(
        self,
        country_id: int,
        skip: int,
        limit: int,
        order: str,
        language: str | None = None,
        publish_year: int | None = None,
    ) -> tuple[list[Vlog], bool]:
        existing_country = await self.repository.get_country_by_id(country_id)
        if existing_country is None:
            raise CountryDoesntExistError()

        vlogs = await self.repository.get_vlogs_by_country_id(
            country_id, skip, limit + 1, order, language, publish_year
        )
        has_more = len(vlogs) > limit
        return vlogs[:limit], has_more
