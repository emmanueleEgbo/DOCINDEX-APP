"""
conftest.py — pytest's shared configuration file.

pytest automatically discovers and loads this file before running any tests.
Anything defined here (fixtures, hooks) is available to ALL test files in this
directory without needing to import it. Think of it as Django's setUp() but
shared across the entire test suite.

Key concepts used here:
What is @pytest.fixture?
It's a decorator that tells pytest: "this function is not a test — it's a reusable setup helper that tests can request."
  
  - @pytest.fixture    : a reusable piece of setup/teardown logic
  - @pytest_asyncio.fixture : same, but for async setup (needed because FastAPI is async)
  - app.dependency_overrides : FastAPI's way to swap real dependencies for fakes during tests
  - ASGITransport      : tells httpx to talk directly to the FastAPI app in-process
                         (no real HTTP server needed — equivalent to Django's test client)
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.api.document_routes import document_router
from app.api.query_routes import query_router
from app.core.database import get_db


@pytest.fixture
def mock_db():
    """
    A fake async database session.

    Instead of the test runner  creating a real test database automatically,
    In FastAPI, we control this ourselves. Here we use AsyncMock — an object
    that pretends to be an async SQLAlchemy session. Any method called on it
    (commit, execute, refresh, etc.) returns another mock by default.

    This fixture is passed into the `client` fixture below, which wires it
    into FastAPI's dependency injection system.
    """
    return AsyncMock()


async def client(mock_db):
    """
    A test HTTP client pre-wired to a minimal FastAPI app, client here is just the test's way of making HTTP requests to your app.
    Instead of doing:
    real browser → real server → real database
    It does:
    fake client → app in memory → fake database

    Why we build a separate app instead of importing app from main.py:
      - main.py has a lifespan() that connects to a real PostgreSQL on startup.
        Using it in tests would require a real running database.
      - Instead, we create a fresh FastAPI app with only the routes we want to
        test, and inject a mock database session. Clean and isolated.

    How dependency injection override works:
      - In production, FastAPI calls get_db() to get a real database session.
      - app.dependency_overrides[get_db] = override_get_db replaces that function
        with our fake version for the duration of the test.
      - Every route that has `db: AsyncSession = Depends(get_db)` will receive
        our mock_db instead of a real connection.

    ASGITransport:
      - FastAPI is an ASGI application (async server gateway interface).
      - ASGITransport lets httpx talk directly to the ASGI app in memory,
        without starting a real HTTP server on a port.
      - Equivalent to Django's `self.client` which bypasses the network layer.
    """