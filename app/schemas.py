from datetime import datetime
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class ResizeArg(BaseModel):
    width: float
    height: float


class CropArg(ResizeArg):
    x: float
    y: float


@dataclass
class Transform:
    resize: ResizeArg | None
    crop: CropArg | None
    rotate: float | None
    format: str | None
    filters: dict[str, bool]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str


class ImageCreate(BaseModel):
    url: str
    name: str
    image_type: str
    size: str
    uploaded_at: datetime


class ImageResponse(ImageCreate):
    pass
