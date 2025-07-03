from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    original_url: HttpUrl

class URLResponse(BaseModel):
    original_url: str
    short_key: str
    short_url: str
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        orm_mode = True