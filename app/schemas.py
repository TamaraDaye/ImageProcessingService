from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ResizeArg(BaseModel):
    width: int
    height: int


class CropArg(BaseModel):
    width: float
    height: float
    x: float
    y: float


class Transform(BaseModel):
    resize: ResizeArg | None = None
    crop: CropArg | None = None
    rotate: float | None = None
    format: Literal["PNG", "JPEG", "JPG", "WEBP"] | None = None
    filters: dict[str, bool] = {"grayscale": False}


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
