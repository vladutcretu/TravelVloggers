from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class VloggerYoutubeData(BaseModel):
    youtube_channel_id: str = Field(max_length=255)
    youtube_channel_name: str = Field(max_length=255)
    youtube_channel_url: str = Field(max_length=255)
    youtube_avatar_url: str = Field(max_length=255)
    youtube_subscribers_count: int


class VloggerYoutubeUploadsId(BaseModel):
    youtube_uploads_id: str = Field(max_length=50)


class VloggerBase(VloggerYoutubeUploadsId, VloggerYoutubeData):
    pass


class VloggerCreate(VloggerBase):
    pass


class VloggerResponse(VloggerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
