from app.models import Base
from app.config import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

try:
    engine = create_async_engine(settings.database_url, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
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
