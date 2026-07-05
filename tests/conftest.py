import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from datetime import datetime, timedelta
from uuid import uuid4

from backend.main import app
from backend.api.dependencies import get_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        pass

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_delete=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()
