from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, status, HTTPException, Query, Form, File, UploadFile, Path
from .. import schemas
from . import authorization
from ..models import models
from .. import utils
from ..database.database import SessionDep


router = APIRouter(tags=["images"])


@router.post("/images", response_model=schemas.ImageResponse)
async def upload_image(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[models.User, Depends(authorization.get_current_user)],
    session: SessionDep,
):
    print(file.filename)

    await file.seek(0)

    image = await utils.upload_image(current_user.username, file)

    db_image = models.Image(user_id=current_user.id, **image.model_dump())

    session.add(db_image)

    await session.flush()

    await session.commit()

    await session.refresh(db_image)

    return db_image


@router.get("/images/{id}")
async def get_image(id: Annotated[int, Path()]):
    pass
