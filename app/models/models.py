from __future__ import annotations
import datetime
from . import Base
from typing import List
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    MapperEvents,
    mapped_column,
    Mapped,
    relationship,
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    images: Mapped[List[Image]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    size: Mapped[float]
    image_type: Mapped[str]
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="images", lazy="selectin")
