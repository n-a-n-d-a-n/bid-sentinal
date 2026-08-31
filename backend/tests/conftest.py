"""
Shared Pytest Fixtures for PROCUREX Test Suite.
"""
import pytest
import asyncio
import os

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def app():
    """Create test FastAPI application."""
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_procurex.db"
    os.environ["ENABLE_DEMO_MODE"] = "true"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-production"
    os.environ["REDIS_URL"] = "redis://localhost:6379/15"
    os.environ["MINIO_ENDPOINT"] = "localhost:9999"

    from app.main import app as fastapi_app
    return fastapi_app

@pytest.fixture(scope="session")
async def async_client(app):
    """Async HTTP test client."""
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
async def db_session():
    """In-memory SQLite session for tests."""
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_procurex.db"

    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    from app.models import Base  # ensure all models are registered

    engine = create_async_engine("sqlite+aiosqlite:///./test_procurex.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("test_procurex.db"):
        os.remove("test_procurex.db")
