from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.dataclasses import dataclass


class ResizeArg(BaseModel):
    width: int | None
    height: int | None


class CropArg(ResizeArg):
    x: int | None
    y: int | None


@dataclass
class Transform:
    resize: ResizeArg
    crop: CropArg
    rotate: int | None
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


class S3ImageData(BaseModel):
    url: str
    name: str
    size: float | int = Field(alias="ContentLength")
    image_type: str = Field(alias="ContentType")
    uploaded_at: datetime = Field(alias="LastModified")


class ImageCreate(BaseModel):
    url: str
    name: str
    image_type: str
    size: float | int
    uploaded_at: datetime


class ImageResponse(ImageCreate):
    pass
