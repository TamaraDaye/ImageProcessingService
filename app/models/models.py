from __future__ import annotations
import datetime
import asyncio
from . import Base
from typing import List
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str]
    image: Mapped[List["Image"]] = relationship(
        back_populates="users", cascade="all, delete-orphan"
    )


class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(200), nullable=True)
    image_name: Mapped[str] = mapped_column(String(200))
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="images")
