from datetime import datetime

from pydantic import BaseModel


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
