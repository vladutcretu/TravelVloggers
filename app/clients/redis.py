from redis.asyncio import Redis

from app.schemas.v2.vlog import VlogYouTubeUploads


class YouTubeUploadsCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, vlogger_id: int) -> str:
        return f"youtube_uploads:{vlogger_id}"

    async def set(self, vlogger_id: int, value: VlogYouTubeUploads) -> None:
        await self.redis.set(
            name=self._key(vlogger_id),
            value=value.model_dump_json(),
            ex=3600 * 24 * 7,  # expiring after 1 week
        )

    async def get(self, vlogger_id: int) -> VlogYouTubeUploads | None:
        data = await self.redis.get(self._key(vlogger_id))

        if not data:
            return None

        return VlogYouTubeUploads.model_validate_json(data)

    async def invalidate(self, vlogger_id: int) -> None:
        await self.redis.delete(self._key(vlogger_id))
