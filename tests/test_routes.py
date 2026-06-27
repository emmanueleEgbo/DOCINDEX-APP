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


@pytest.fixture
def sample_summary():
    """A fake DocumentSummary that mocked service functions return."""
    return DocumentSummary(
        source_document_id="abc-123",
        title="Test Document",
        source="test",
        chunk_count=5,
        created_at=datetime.utcnow(),
    )

@pytest.fixture
def sample_indexing_response():
    """A fake IndexingResponse that the mocked index_document returns."""
    return IndexingResponse(
        source_document_id="abc-123",
        title="Test Document",
        chunk_count=5,
        message="Document indexed successfully into 5 chunks.",
    )


class TestIndexDocumentRoute:
    async def test_returns_201_on_success(self, client, valid_body, sample_indexing_response):
        """
        Happy path: valid request body → service returns success → route returns 201.

        patch() here replaces the real index_document function with an AsyncMock
        that immediately returns our fake response. The route handler doesn't know
        it's talking to a mock — it just gets back the IndexingResponse and returns it.
        """
        with patch("app.services.document_service.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = sample_indexing_response
            response = await client.post("/v1/documents", json=valid_body)

        assert response.status_code == 201
        data = response.json()
        assert data["source_document_id"] == "abc-123"
        assert data["chunk_count"] == 5
    
    async def test_returns_422_on_empty_content(self, client):
        """
        422 Unprocessable Entity — Pydantic validation rejects the request
        BEFORE it even reaches the route handler. No mocking needed because
        the service is never called.
        """
        response = await client.post("/v1/documents", json={
            "title": "Test",
            "content": "",  # rejected by @field_validator in DocumentCreate
        })
        assert response.status_code == 422
    
    async def test_returns_422_on_whitespace_content(self, client):
        response = await client.post("/v1/documents", json={
            "title": "Test",
            "content": "   ",
        })
        assert response.status_code == 422