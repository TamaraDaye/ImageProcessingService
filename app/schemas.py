from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, model_validator


class Resize(BaseModel):
    width: int
    height: int


class Crop(BaseModel):
    left: float
    upper: float
    right: float
    lower: float


class Transform(BaseModel):
    resize: Optional[Resize] = None
    crop: Optional[Crop] = None
    rotate: Optional[float] = None
    format: Literal["PNG", "JPEG", "JPG", "WEBP"] | str = "JPEG"
    filters: dict[str, bool] = {"grayscale": False}

    @model_validator(mode="after")
    def clean_data(self):
        if self.resize and (self.resize.width <= 0 or self.resize.height <= 0):
            self.resize = None

        if self.rotate is not None:
            if self.rotate == 0.0 or abs(self.rotate) == 360.0:
                self.rotate = None

        if self.crop and (
            self.crop.left <= 0.0
            and self.crop.right <= 0.0
            and self.crop.upper <= 0
            and self.crop.left <= 0
        ):
            self.crop = None

        return self


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
