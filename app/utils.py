from datetime import datetime, timezone
from pwdlib import PasswordHash
import aioboto3
from . import schemas
from .config import settings
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

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
