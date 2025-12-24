from pydantic import BaseModel
from typing import Dict, Any

class UploadRequestResponse(BaseModel):
    interest: str
    topic: str
    user_id: str
    upload_url: str
    upload_method: str = "PUT"  # HTTP method to use for upload
    upload_fields: Dict[str, Any] | None = None  # For POST multipart uploads
    video_path: str

class VideoReadResponse(BaseModel):
    user_id: str
    video_path: str
    download_url: str
