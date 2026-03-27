import aiohttp
from datetime import datetime

from fastapi import status

from app.schemas.vlog import VlogYouTubeVideoData
from app.core.config import settings


class YoutubeDataNotFoundError(Exception):
    pass


class YoutubeClient:
    """
    Mapped data from YouTube Data API v3 videos endpoint.

    Expected API response:
    {
        "items": [
            {
                "id": "11-char string",
                "snippet": {
                    "publishedAt": "datetime",
                    "title": "string",
                    "thumbnails": {
                        "medium": {"url": "string"}
                    },
                    "defaultLanguage": "2-char string"
                }
            }
        ]
    }

    More details about YouTube DATA API v3: https://developers.google.com/youtube/v3/
    """

    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3/videos"
        self.api_key = settings.YOUTUBE_APP_API_KEY

    async def get_video_data(self, video_id: str) -> VlogYouTubeVideoData | None:
        params = {
            "id": video_id,
            "key": self.api_key,
            "part": "snippet",
            "fields": "items(id, snippet(publishedAt, title, thumbnails.medium.url, defaultLanguage))",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.base_url, params=params) as response:
                if response.status != status.HTTP_200_OK:
                    raise YoutubeDataNotFoundError(
                        f"Youtube video with ID: {video_id} not found"
                    )
                data = await response.json()

        items = data.get("items")
        if not items:
            raise YoutubeDataNotFoundError(
                f"Youtube video ID: {video_id} not returned any data"
            )
        if items[0]["id"] != video_id:
            raise YoutubeDataNotFoundError(
                f"Youtube video ID: {video_id} not equal to returned id"
            )

        snippet = items[0]["snippet"]
        return VlogYouTubeVideoData(
            published_at=datetime.fromisoformat(
                snippet["publishedAt"].replace("Z", "+00:00")  # "datetime" -> datetime
            ),
            title=snippet["title"],
            thumbnail_url=snippet["thumbnails"]["medium"]["url"],
            language=snippet["defaultLanguage"],
        )
