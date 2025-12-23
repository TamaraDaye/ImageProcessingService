"""Database connectivity Module"""

from typing import Annotated
from app.models import Base
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import Depends

try:
    engine = create_async_engine(settings.database_url)
except Exception as e:
    print(e)
    raise e


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise e


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
