from pwdlib import PasswordHash
import aioboto3
import aiofiles

password_hash = PasswordHash.recommended()


async def verify_password(hashed_password, password):
    return password_hash.verify(hashed_password, password)


def hash_password(password):
    return password_hash.hash(password)
