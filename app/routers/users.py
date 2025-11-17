from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, UploadFile, Form
from ..database.database import SessionDep
from .. import schemas
from .. import utils
from ..models import models

router = APIRouter(tags=["users"])  # pyright: ignore[]




@router.get("/user", response_model=schemas.UserResponse)
async def get_current_user()



@router.post("/signup/", response_model=schemas.UserResponse)
async def create_user(
    user_data: Annotated[schemas.UserCreate, Form()], session: SessionDep
):
    user_data.password = utils.hash_password(user_data.password)
    db_user = models.User(**user_data.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
