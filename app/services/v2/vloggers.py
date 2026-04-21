from app.repositories.v2.vloggers import VloggersRepository
from app.core.exceptions import (
    VloggerDoesntExistError,
    VloggerUploadsError,
    YoutubeDataNotFoundError,
)
from app.clients.youtube import YoutubeClient


class VloggersService:
    def __init__(self, repository: VloggersRepository):
        self.repository = repository

    async def get_youtube_uploads(self, user_id: int):
        vlogger = await self.repository.get_vlogger_by_user_id(user_id)

        if not vlogger:
            raise VloggerDoesntExistError()

        if not vlogger.youtube_uploads_id:
            raise VloggerUploadsError()

        try:
            youtube_videos = await YoutubeClient.get_uploaded_videos(
                vlogger.youtube_uploads_id
            )
        except YoutubeDataNotFoundError:
            raise YoutubeDataNotFoundError

        return youtube_videos
