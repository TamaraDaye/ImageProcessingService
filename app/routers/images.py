from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, status, HTTPException, Query, Form, File, UploadFile
from . import authorization
from ..models import models
from .. import utils


router = APIRouter(tags=["images"])


@router.post("/images")
async def upload_image(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[models.User, Depends(authorization.get_current_user)],
):
    await file.seek(0)

    await utils.upload_image(current_user.username, file)

    return "Done"
