from pydantic import BaseModel
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


class FormData(BaseModel):
    pass
