"""
Integration tests for document API routes.

These tests send real HTTP requests (via httpx) to the FastAPI app and check
the HTTP responses — status codes, response bodies, and error formats.

"Integration" here means we test the full request/response cycle through the
route handler, but we mock the service layer beneath it. The routes don't know
or care that the service is mocked — they just call it and return the result.

Why mock the service and not the DB directly?
  - Routes call services. Services call repositories. Repositories call the DB.
  - By mocking at the service layer, we test only the route's responsibility:
    parsing input → calling the service → shaping the HTTP response.
  - The service itself is tested separately in test_document_service.py.
  - This is the "test one layer at a time" principle.

The `client` fixture (from conftest.py) provides an httpx.AsyncClient connected
to our test FastAPI app. It is injected automatically by pytest.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.schemas.document_schema import DocumentSummary, IndexingResponse


@pytest.fixture
def valid_body():
    """A valid POST /v1/documents request body."""
    return {
        "title": "Test Document",
        "content": "This is meaningful content for testing the indexing pipeline.",
        "source": "test",
    }

