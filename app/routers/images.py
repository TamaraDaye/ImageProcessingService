from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse
from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, status, HTTPException, Query, File, UploadFile, Path
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
    await file.seek(0)

    image = await utils.upload_image(current_user.username, file)

    db_image = models.Image(user_id=current_user.id, **image.model_dump())

    session.add(db_image)

    await session.flush()

    await session.commit()

    await session.refresh(db_image)

    return db_image


@router.get("/images/{id}", response_class=StreamingResponse)
async def get_image(
    id: Annotated[int, Path()],
    current_user: Annotated[models.User, Depends(authorization.get_current_user)],
    session: SessionDep,
):
    db_image = await session.get(models.Image, id)

    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        image_iterator = utils.retrieve_image(current_user.username, db_image.name)  # pyright: ignore[]

        return StreamingResponse(image_iterator, media_type=db_image.image_type)

    except ClientError as _:
        raise HTTPException(status_code=404, detail="Image not found")


@router.post("/images/{id}/transform", response_model=schemas.ImageResponse)
async def transform_image(
    id: Annotated[int, Path()],
    current_user: Annotated[models.User, Depends(authorization.get_current_user)],
    transformations: Annotated[schemas.Transform, Query()],
):
    pass
