from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class VlogYouTubeUploadData(BaseModel):
    video_id: str
    published_at: datetime
    title: str
    thumbnail_url: str


class VlogYouTubeUploads(BaseModel):
    next_page_token: str | None = None
    prev_page_token: str | None = None
    total_results: int
    results_per_page: int
    uploads: list[VlogYouTubeUploadData]


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


class CountryData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    iso_code: str
    has_vlog: bool
