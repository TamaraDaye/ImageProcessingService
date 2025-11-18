from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from . import authorization
from ..database.database import SessionDep
from .. import utils
from ..models import models


router = APIRouter(tags=["login"])


@router.post("/login")
async def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    stmt = select(models.User).where(models.User.email == user_data.username)
    user = await session.scalar(stmt)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid User creditentials",
        )

    if not utils.verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user creditentials",
        )

    return authorization.create_access_token(data={"user_id": user.id})
