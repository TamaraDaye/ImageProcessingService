from pwdlib import PasswordHash
import aioboto3
from .config import settings
import aiofiles

password_hash = PasswordHash.recommended()


async def verify_password(hashed_password: str, password: str):
    return password_hash.verify(hashed_password, password)


def hash_password(password: str):
    return password_hash.hash(password)


async def upload_image(username: str, image):
    bucket = settings.s3_bucket
    prefix = f"{username}/"

    session = aioboto3.Session()

    async with session.client("s3") as s3:  # pyright: ignore[]
        key = f"{prefix}{image.filename}"
        await s3.upload_fileobj(image.file, bucket, key)

    return True
