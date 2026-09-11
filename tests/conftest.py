import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app, Base
from src.database import DATABASE_URL
from src.database import get_session 

@pytest.fixture
async def db_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
def app_with_test_db(db_engine):
    AsyncSessionLocal = async_sessionmaker(db_engine, expire_on_commit=False)

    async def test_get_session():
        async with AsyncSessionLocal() as session:
            yield session

    # Подменяем именно get_session, а не SessionDep
    app.dependency_overrides[get_session] = test_get_session
    yield app
    app.dependency_overrides.clear()
