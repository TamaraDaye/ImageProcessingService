"""Module for creating database tables from orm"""

from __future__ import annotations
import datetime
from . import Base
from typing import List
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
)


class User(Base):
    """
    User class will map to a "users" table
    in the table when created
    :Columns - id, email, username, password
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    images: Mapped[List[Image]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Image(Base):
    """
    Image class will to map to an "images table"
    in the database when created
    :Columns -id, url, name, size, image_type, uploaded_at, user_id-foreignkey delineates owner of image record from users table
    many to one relationship to users table
    """

    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(200), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    size: Mapped[str]
    image_type: Mapped[str]
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="images", lazy="selectin")
