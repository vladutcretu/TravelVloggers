from app.repositories.v2.vloggers import VloggersRepository
from app.clients.redis import YouTubeUploadsCache
from app.schemas.v2.vlog import VlogYouTubeUploads
from app.core.exceptions import (
    VloggerDoesntExistError,
    VloggerUploadsError,
    YoutubeDataNotFoundError,
)
from app.clients.youtube import YoutubeClient


class VloggersService:
    def __init__(self, repository: VloggersRepository, cache: YouTubeUploadsCache | None = None):
        self.repository = repository
        self.cache = cache

    async def get_youtube_uploads(self, user_id: int) -> VlogYouTubeUploads:
        vlogger = await self.repository.get_vlogger_by_user_id(user_id)

        if not vlogger:
            raise VloggerDoesntExistError()

        if not vlogger.youtube_uploads_id:
            raise VloggerUploadsError()
        
        if self.cache:
            cached = await self.cache.get(vlogger.id)
            if cached:
                return cached
            else:
                try:
                    youtube_client = YoutubeClient()
                    youtube_uploads = await youtube_client.get_uploaded_videos(
                        vlogger.youtube_uploads_id
                    )
                except YoutubeDataNotFoundError as e:
                    raise e
                await self.cache.set(vlogger.id, youtube_uploads)

        return youtube_uploads
