from datetime import datetime, timezone
from pwdlib import PasswordHash
import aioboto3
from sqlalchemy import tuple_
from . import schemas
from .config import settings
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from PIL import Image, ImageOps

password_hash = PasswordHash([Argon2Hasher(), BcryptHasher()])


def format_size(size_bytes, decimals=2):
    if size_bytes == 0:
        return "O bytes"
    power = 1024

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]

    import math

    i = int(math.floor(math.log(size_bytes, power)))

    return f"{size_bytes / (power**i):.{decimals}f} {units[i]}"


async def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)


def hash_password(password: str):
    return password_hash.hash(password)


async def upload_image(username: str, image):
    bucket = settings.s3_bucket
    prefix = f"{username}/"

    session = aioboto3.Session()

    image.file.seek(0, 2)

    file_size_bytes = image.file.tell()

    image.file.seek(0)

    size_mb = format_size(file_size_bytes)

    async with session.client("s3") as s3:  # pyright: ignore[]
        key = f"{prefix}{image.filename}"
        await s3.upload_fileobj(
            image.file, bucket, key, ExtraArgs={"ContentType": image.content_type}
        )

    return schemas.ImageCreate(
        name=image.filename,
        image_type=image.content_type,
        url=f"https://{bucket}.s3.amazonaws.com/{key}",
        size=size_mb,
        uploaded_at=datetime.now(timezone.utc),
    )


async def retrieve_image(username: str, image_name: str):
    bucket = settings.s3_bucket
    key = f"{username}/{image_name}"

    session = aioboto3.Session()

    async with session.client("s3") as s3:  # pyright: ignore[]
        response = await s3.get_object(Bucket=bucket, Key=key)

        async for chunk in response["Body"]:
            yield chunk


async def image_transformer(img, transformations, image_name):
    with Image.open(img) as img:
        new_image = img
        new_image_name = image_name

        if transformations["resize"] is not None:
            new_size = tuple(transformations["resize"].values())

            new_image = new_image.resize(new_size)

            new_image_name = "resized_" + new_image_name

        if transformations["crop"] is not None:
            box = tuple(transformations["crop"].values())

            new_image = new_image.crop(box)

            new_image_name = "cropped_" + new_image_name

        if transformations["rotate"] is not None:
            angle = transformations["rotate"]

            new_image = new_image.rotate(angle)

            new_image_name = "rotated_" + new_image_name

        if transformations["filters"] is not None:
            if transformations["filters"]["grayscale"]:
                new_image = ImageOps.grayscale(new_image)
                new_image_name = "grayscale_" + new_image_name

        try:
            if new_image.mode in ("RGBA", "P"):
                new_image = new_image.convert("RGB")
        except:
            pass
