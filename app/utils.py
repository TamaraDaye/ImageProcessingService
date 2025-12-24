from datetime import datetime, timezone
from fastapi import HTTPException, status
from pwdlib import PasswordHash
import aioboto3
from botocore.exceptions import ClientError
from . import schemas
from .config import settings
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from PIL import Image, ImageOps
import io

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


async def upload_image(username: str, image_data, image_name, image_type):
    bucket = settings.s3_bucket
    prefix = f"{username}/"

    session = aioboto3.Session()

    image_data.seek(0, 2)

    file_size_bytes = image_data.tell()

    image_data.seek(0)

    size_mb = format_size(file_size_bytes)

    async with session.client("s3") as s3:  # pyright: ignore[]
        key = f"{prefix}{image_name}"
        try:
            await s3.upload_fileobj(
                image_data, bucket, key, ExtraArgs={"ContentType": image_type}
            )
        except ClientError as e:
            raise

    return schemas.ImageCreate(
        name=image_name,
        image_type=image_type,
        url=f"https://{bucket}.s3.amazonaws.com/{key}",
        size=size_mb,
        uploaded_at=datetime.now(timezone.utc),
    )


async def retrieve_image(username: str, image_name: str, stream=False):
    bucket = settings.s3_bucket
    key = f"{username}/{image_name}"

    session = aioboto3.Session()

    async with session.client("s3") as s3:  # pyright: ignore[]
        try:
            response = await s3.get_object(Bucket=bucket, Key=key)
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't retrieve_image"
            )

        async with response["Body"] as body:
            if stream:
                async for chunk in body.iter_chunks():
                    yield chunk

            else:
                yield await body.read()


async def image_transformer(img, transformations, image_name):
    img.seek(0)

    with Image.open(img) as img:
        img.load()
        new_image = img.copy()
        new_image_name = image_name
        new_image_type = transformations.format or img.format

        if new_image_type:
            new_image_type = new_image_type.upper()

        if transformations.resize:
            width = transformations.resize.width
            height = transformations.resize.height

            resized = new_image.resize((width, height))

            new_image = resized

            new_image_name = "resized_" + new_image_name

        if transformations.crop:
            box = tuple(transformations.crop.model_dump().values())
            print(box)

            new_image = new_image.crop(box)

            new_image_name = "cropped_" + new_image_name

        if transformations.rotate:
            angle = transformations.rotate

            new_image = new_image.rotate(angle)

            new_image_name = "rotated_" + new_image_name

        if transformations.filters:
            if transformations.filters["grayscale"]:
                new_image = ImageOps.grayscale(new_image)
                new_image_name = "grayscale_" + new_image_name

        if new_image_type.upper() in ["JPG", "JPEG"]:  # pyright: ignore[]
            if new_image.mode in ("RGBA", "P"):
                new_image = new_image.convert("RGB")

        img_byte_arr = io.BytesIO()

        try:
            new_image.save(img_byte_arr, format=new_image_type)
            img_byte_arr.seek(0)
            return {
                "name": new_image_name,
                "type": f"image/{new_image_type.lower()}",  # pyright: ignore[]
                "data": img_byte_arr,
            }

        except Exception as e:
            print(f"Transformation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Transformation failed"
            )
