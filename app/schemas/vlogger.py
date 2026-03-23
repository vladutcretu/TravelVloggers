from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class VloggerBase(BaseModel):
    youtube_channel_id: str = Field(max_length=255)
    youtube_channel_name: str = Field(max_length=255)
    youtube_channel_url: str = Field(max_length=255)
    youtube_avatar_url: str = Field(max_length=255)


class VloggerCreate(VloggerBase):
    pass


class VloggerResponse(VloggerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
