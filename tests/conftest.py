import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.db.connection import Base, get_db
from main import app


DB_TEST_URL = (
    settings.DATABASE_TEST_URL
    or f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@localhost:5433/{settings.POSTGRES_DB_TEST}"
)


@pytest.fixture(scope="session")
async def test_engine():
    """
    Create a test engine for every single pytest session.
    DB tables are created when tests starts and dropped when tests are finished.
    """
    engine = create_async_engine(url=DB_TEST_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    """
    Create a test session for every single test.
    Data are just savepointed, not commited, and DB is rollbacked when test is finished.
    """
    async with test_engine.connect() as connection:
        await connection.begin()

        session_factory = async_sessionmaker(
            connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with session_factory() as session:
            yield session

        await connection.rollback()


@pytest.fixture(scope="function")
async def client(db_session):
    """
    Override get_db method from FastAPI app's to a method that returns the test session.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
