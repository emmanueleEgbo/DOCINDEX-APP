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