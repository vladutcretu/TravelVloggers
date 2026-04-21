from datetime import datetime

import aiohttp
from fastapi import status

from app.schemas.v1.vlog import VlogYouTubeVideoData
from app.schemas.v2.vlogger import VloggerYoutubeData, VloggerYoutubeUploadsId
from app.core.config import settings
from app.core.exceptions import YoutubeDataNotFoundError


class YoutubeClient:
    """
    Fetch data from YouTube Data API v3 endpoints.
    More details about YouTube Data API v3: https://developers.google.com/youtube/v3/
    """

    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = settings.YOUTUBE_APP_API_KEY

    async def get_video_data(self, video_id: str) -> VlogYouTubeVideoData:
        """
        Fetch snippet for video data.
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
        Returns mapped data (for Vlog model):
            - published_at
            - title
            - thumbnail_url
            - language
        """
        params = {
            "id": video_id,
            "key": self.api_key,
            "part": "snippet",
            "fields": "items(id, snippet(publishedAt, title, thumbnails.medium.url, defaultLanguage))",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"{self.base_url}/videos", params=params
            ) as response:
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

    async def get_channel_data(self, access_token: str) -> VloggerYoutubeData:
        """
        Fetch snippet + statistics for the authenticated user's channel.
        Expected API response:
        {
            "items": [
                {
                    "id": "channel_id",
                    "snippet": {
                        "title": "channel_name",
                        "thumbnails": {
                        "default": { "url": "avatar_url" }
                        }
                    },
                    "statistics": {
                        "subscriberCount": int
                    }
                }
            ]
        }
        Returns mapped data (for Vlogger model):
            - youtube_channel_id
            - youtube_channel_name
            - youtube_channel_url
            - youtube_avatar_url
            - youtube_subscribers_count
        """
        params = {
            "key": self.api_key,
            "part": "snippet,statistics",
            "mine": "true",
        }
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            raise YoutubeDataNotFoundError(
                "Youtube channel data cant be retrieved without access token"
            )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"{self.base_url}/channels", headers=headers, params=params
            ) as response:
                data = await response.json()
                print("YouTube response:", data)  # debug
                if response.status != status.HTTP_200_OK:
                    raise YoutubeDataNotFoundError(
                        "Youtube channel data cant be retrieved."
                    )
                data = await response.json()

        items = data.get("items")
        if not items:
            raise YoutubeDataNotFoundError("No channel found for this user")

        item = data["items"][0]
        snippet = item["snippet"]
        statistics = item["statistics"]

        return VloggerYoutubeData(
            youtube_channel_id=item["id"],
            youtube_channel_name=snippet["title"],
            youtube_channel_url=f"https://www.youtube.com/channel/{item['id']}",
            youtube_avatar_url=snippet["thumbnails"]["default"]["url"],
            youtube_subscribers_count=int(statistics.get("subscriberCount", 0)),
        )

    async def get_uploads_id(self, channel_id: str) -> VloggerYoutubeUploadsId:
        """
        Fetch uploads playlist ID for the given channel.
        Expected API response:
        {
            "items": [
                {
                "contentDetails": {
                    "relatedPlaylists": {
                    "uploads": "UPLOADS_ID"
                    }
                }
                }
            ]
        }
        Returns mapped data (for Vlogger model):
            - youtube_uploads_id
        """
        params = {
            "key": self.api_key,
            "part": "contentDetails",
            "id": f"{channel_id}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"{self.base_url}/channels", params=params
            ) as response:
                if response.status != status.HTTP_200_OK:
                    raise YoutubeDataNotFoundError(
                        "Youtube Uploads ID playlist cant be retrieved."
                    )
                data = await response.json()

        items = data.get("items")
        if not items:
            raise YoutubeDataNotFoundError("No contentDetails found for this channel")

        return VloggerYoutubeUploadsId(
            youtube_uploads_id=items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        )
