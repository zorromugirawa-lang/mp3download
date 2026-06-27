from pydantic import BaseModel
from typing import Optional, List

class VideoInfo(BaseModel):
    title: str
    author: str
    length: int
    views: int
    description: str
    thumbnail_url: str
    video_streams: List[dict]
    audio_streams: List[dict]

class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "highest"
    type: Optional[str] = "video"  # video or audio
    filename: Optional[str] = None

class DownloadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    filesize: Optional[int] = None