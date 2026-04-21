from app.repositories.v2.vloggers import VloggersRepository
from app.clients.redis import YouTubeUploadsCache
from app.schemas.v2.vlog import VlogYouTubeUploads
from app.core.exceptions import (
    VloggerDoesntExistError,
    VloggerUploadsError,
    YoutubeDataNotFoundError,
    RateLimitError,
    UserDoesntExistError,
)
from app.clients.youtube import YoutubeClient


class VloggersService:
    def __init__(self, repository: VloggersRepository, cache: YouTubeUploadsCache):
        self.repository = repository
        self.cache = cache

    async def get_youtube_uploads(self, user_id: int) -> VlogYouTubeUploads:
        vlogger = await self.repository.get_vlogger_by_user_id(user_id)

        if not vlogger:
            raise VloggerDoesntExistError()

        if not vlogger.youtube_uploads_id:
            raise VloggerUploadsError()

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

    async def update_youtube_uploads(self, user_id: int) -> VlogYouTubeUploads:
        vlogger = await self.repository.get_vlogger_by_user_id(user_id)

        if not vlogger:
            raise VloggerDoesntExistError()

        if not vlogger.youtube_uploads_id:
            raise VloggerUploadsError()

        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserDoesntExistError()

        # Set rate limit to apply membership status rules: non-membership have max 1 request / 7 days, membership have max 1 request / 1 day
        rate_key = f"update_uploads_limit:{vlogger.id}"

        exists_rate = await self.cache.redis.get(rate_key)
        if exists_rate:
            raise RateLimitError()

        # Set rate limit key if not exists
        ttl = 3600 * 24 * (7 if not user.has_membership_active else 1)
        await self.cache.redis.set(name=rate_key, value="1", ex=ttl)

        # Fresh fetch Youtube client
        try:
            youtube_client = YoutubeClient()
            youtube_uploads = await youtube_client.get_uploaded_videos(
                vlogger.youtube_uploads_id
            )
        except YoutubeDataNotFoundError as e:
            raise e

        # Overwrite cache
        await self.cache.set(vlogger.id, youtube_uploads)

        return youtube_uploads
