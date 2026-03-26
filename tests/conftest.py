import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.db.connection import Base, get_db
from main import app
from app.models.user import User
from app.core.security import create_access_token
from app.models.vlogger import Vlogger
from app.api.dependencies import Pagination, pagination_params
from app.models.vlog import Country


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


# Fixtures for reusability
@pytest.fixture()
async def superuser_token(db_session) -> str:
    """
    Create a superuser account using db_session and return its access token.
    """
    superuser = User(
        email=settings.SUPERUSER_EMAIL, password_hash="123456", is_superuser=True
    )
    db_session.add(superuser)
    await db_session.commit()

    token = create_access_token(data={"sub": str(superuser.id)})
    return token


@pytest.fixture()
async def admin_token(db_session) -> str:
    """
    Create an admin account using db_session and return its access token.
    """
    admin = User(email="admin@mail.com", password_hash="123456", is_admin=True)
    db_session.add(admin)
    await db_session.commit()

    token = create_access_token(data={"sub": str(admin.id)})
    return token


@pytest.fixture()
async def user_token(db_session) -> str:
    """
    Create a standard user account using db_session and return its access token.
    """
    user = User(email="user@mail.com", password_hash="123456")
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(data={"sub": str(user.id)})
    return token


@pytest.fixture()
async def superuser(db_session) -> User:
    """
    Create a superuser account using db_session and return it.
    """
    superuser = User(email=settings.SUPERUSER_EMAIL, password_hash="123456")
    db_session.add(superuser)
    await db_session.commit()
    return superuser


@pytest.fixture()
async def admin(db_session) -> User:
    """
    Create an admin account using db_session and return it.
    """
    admin = User(email="admin@mail.com", password_hash="123456", is_admin=True)
    db_session.add(admin)
    await db_session.commit()
    return admin


@pytest.fixture()
async def user(db_session) -> User:
    """
    Create a standard user account using db_session and return it.
    """
    user = User(email="user@mail.com", password_hash="123456")
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture()
async def vlogger(db_session) -> Vlogger:
    """
    Create a vlogger instance using db_session and return it.
    """
    vlogger = Vlogger(
        youtube_channel_id="test_channel_id",
        youtube_channel_name="test_channel_name",
        youtube_channel_url="test_channel_url",
        youtube_avatar_url="test_avatar_url",
    )
    db_session.add(vlogger)
    await db_session.commit()
    return vlogger


@pytest.fixture()
async def pagination() -> Pagination:
    """
    Read default values for pagination params (skip, limit and order) and return they.
    """
    return pagination_params()


@pytest.fixture()
async def vloggers_factory(db_session):
    """
    Create multiple vlogger instances using db_session and return it.
    """

    async def _create_vloggers(instances: int = 15) -> list[Vlogger]:
        vloggers_list = []
        for i in range(instances):
            vlogger = Vlogger(
                youtube_channel_id=f"id_{i}",
                youtube_channel_name=f"name_{i}",
                youtube_channel_url=f"url_{i}",
                youtube_avatar_url=f"avatar_{i}",
            )
            db_session.add(vlogger)
            vloggers_list.append(vlogger)

        await db_session.commit()

        for vlogger in vloggers_list:
            await db_session.refresh(vlogger)

        return vloggers_list

    return _create_vloggers


@pytest.fixture()
async def countries_factory(db_session):
    """
    Create multiple country instances using db_session and return it.
    """

    import string
    from itertools import product

    letters = string.ascii_uppercase
    iso_codes = ["".join(p) for p in product(letters, repeat=2)]

    async def _create_countries(instances: int = 15) -> list[Country]:
        countries_list = []
        for i in range(instances):
            country = Country(
                name=f"Name #{i}",
                iso_code=iso_codes[i],
            )
            db_session.add(country)
            countries_list.append(country)

        await db_session.commit()

        for country in countries_list:
            await db_session.refresh(country)

        return countries_list

    return _create_countries
