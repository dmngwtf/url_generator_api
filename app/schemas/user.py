from pydantic import BaseModel
from typing import List
from .url import URLResponse

class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    urls: List[URLResponse] = []

    class Config:
        orm_mode = True