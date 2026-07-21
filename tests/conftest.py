import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import event
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from uuid import uuid4

from backend.main import app
from backend.api.dependencies import get_db
from config.database_config import Base
from backend.models import *  # noqa: F401, F403


# Register UUID type for SQLite (used in tests with in-memory SQLite)
@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"


# Register JSONB type for SQLite (uses JSON text)
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "VARCHAR(500)"


def _register_sqlite_functions(dbapi_connection, connection_record):
    """Register custom SQLite functions like variance."""
    try:
        # Try accessing the raw sqlite3 connection through various adapter layers
        raw = dbapi_connection
        if hasattr(raw, "driver_connection"):
            raw = raw.driver_connection
        # aiosqlite Connection stores sqlite3.Connection as _conn
        if hasattr(raw, "_conn"):
            raw = raw._conn

        class VarianceFunc:
            def __init__(self):
                self.values = []

            def step(self, value):
                if value is not None:
                    self.values.append(float(value))

            def finalize(self):
                if len(self.values) < 2:
                    return 0.0
                mean = sum(self.values) / len(self.values)
                return sum((x - mean) ** 2 for x in self.values) / (len(self.values) - 1)

        raw.create_aggregate("variance", 1, VarianceFunc)
    except Exception:
        pass  # Skip if we can't register the function; tests will xfail gracefully


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

    event.listen(engine.sync_engine, "connect", _register_sqlite_functions)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()
