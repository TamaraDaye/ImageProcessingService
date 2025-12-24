from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse
from typing import Annotated
from fastapi import APIRouter, Body
from fastapi import Depends, status, HTTPException, Query, File, UploadFile, Path
from .. import schemas
from . import authorization
from ..models import models
from .. import utils
from ..database.database import SessionDep
import io


router = APIRouter(tags=["images"])


@router.post("/images", response_model=schemas.ImageResponse)
async def upload_image(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[models.User, Depends(authorization.get_current_user)],
    session: SessionDep,
):
    await file.seek(0)

    image = await utils.upload_image(
        current_user.username, file, file.filename, file.content_type
    )

    db_image = models.Image(user_id=current_user.id, **image.model_dump())

    session.add(db_image)

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
    transformations: schemas.Transform,
    session: SessionDep,
):
    img_data = io.BytesIO()

    db_image = await session.get(models.Image, id)

    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        async for chunk in utils.retrieve_image(current_user.username, db_image.name):
            img_data.write(chunk)

    except Exception as e:
        print(f"Coudn't retrieve_image {e}")

    transformed = await utils.image_transformer(
        img_data, transformations, db_image.name
    )

    if not transformed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="image transformation failed",
        )

    db_transformed_image = await utils.upload_image(
        current_user.username,
        transformed["data"],
        transformed["name"],
        transformed["type"],
    )

    db_transformed_image = models.Image(
        user_id=current_user.id, **db_transformed_image.model_dump()
    )

    session.add(db_transformed_image)

    await session.commit()

    await session.refresh(db_transformed_image)

    return db_transformed_image
