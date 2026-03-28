from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CountryBase(BaseModel):
    id: int
    name: str = Field(max_length=50)
    iso_code: str = Field(min_length=2, max_length=2, pattern="^[A-Z]{2}$")


class CountryResponse(CountryBase):
    model_config = ConfigDict(from_attributes=True)


class CountryResponsePaginated(BaseModel):
    countries: list[CountryResponse]
    skip: int
    limit: int
    has_more: bool


class VlogBase(BaseModel):
    vlogger_id: int
    country_id: int
    youtube_video_id: str = Field(min_length=11, max_length=11)


class VlogCreate(VlogBase):
    pass


class VlogYouTubeVideoData(BaseModel):
    published_at: datetime
    title: str
    thumbnail_url: str
    language: str | None = None


class VlogResponse(VlogBase, VlogYouTubeVideoData):
    model_config = ConfigDict(from_attributes=True)

    youtube_video_url: str
    id: int
    created_at: datetime


class VlogUpdate(BaseModel):
    vlogger_id: int | None = None
    country_id: int | None = None
