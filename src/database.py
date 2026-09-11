from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from databases import Database
from config import settings

DATABASE_URL = settings.DATABASE_URL

database = Database(DATABASE_URL)

engine = create_async_engine(DATABASE_URL)

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session