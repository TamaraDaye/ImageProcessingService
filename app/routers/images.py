from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    Query,
    File,
    UploadFile,
    Path,
)
from sqlalchemy import text
from sqlalchemy.future import select
from .. import schemas
from . import authorization
from ..models import models
from .. import utils
from ..database.database import SessionDep, redis
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

    cached_image = await redis.get(db_image.name)

    if cached_image:
        return StreamingResponse(
            io.BytesIO(cached_image), media_type=db_image.image_type
        )

    try:
        img_data = io.BytesIO()

        async for chunk in utils.retrieve_image(current_user.username, db_image.name):
            img_data.write(chunk)

        image_bytes = img_data.getvalue()

        await redis.set(db_image.name, image_bytes)

        img_data.seek(0)

        return StreamingResponse(img_data, media_type=db_image.image_type)

    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/images/", response_model=list[schemas.ImageResponse])
async def get_images(
    session: SessionDep, pagination: Annotated[schemas.Pagination, Query()]
):
    query = (
        select(models.Image)
        .limit(pagination.per_page)
        .offset(
            pagination.page - 1
            if pagination.page == 1
            else (pagination.page - 1) * pagination.per_page
        )
        .order_by(text(f"uploaded_at {pagination.order}"))
    )

    images = await session.scalars(query)

    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return images


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    async for chunk in utils.retrieve_image(current_user.username, db_image.name):
        img_data.write(chunk)

    transformed = await utils.image_transformer(
        img_data, transformations, db_image.name
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
