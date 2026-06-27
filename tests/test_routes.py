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
    
    async def test_returns_422_on_missing_title(self, client):
        # `title` is a required field — omitting it causes a 422
        response = await client.post("/v1/documents", json={"content": "Some content."})
        assert response.status_code == 422
    
    async def test_returns_502_on_embedding_api_failure(self, client, valid_body):
        """
        If the OpenAI embedding API fails, the service raises RuntimeError.
        The route handler catches this and returns 502 Bad Gateway.
        This test verifies that error mapping is correct.
        """
        with patch("app.services.document_service.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.side_effect = RuntimeError("OpenAI timeout")
            response = await client.post("/v1/documents", json=valid_body)

        assert response.status_code == 502


class TestListDocumentsRoute:
    async def test_returns_200_with_document_list(self, client, sample_summary):
        with patch("app.services.document_service.get_all_documents", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [sample_summary]
            response = await client.get("/v1/documents")

        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Test Document"

    async def test_returns_empty_list_when_no_documents(self, client):
        # An empty database is a valid state — returns 200 with []
        with patch("app.services.document_service.get_all_documents", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            response = await client.get("/v1/documents")

        assert response.status_code == 200
        assert response.json() == []


class TestGetDocumentRoute:
    async def test_returns_200_when_document_found(self, client, sample_summary):
        with patch("app.services.document_service.get_document_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_summary
            response = await client.get("/v1/documents/abc-123")

        assert response.status_code == 200
        assert response.json()["source_document_id"] == "abc-123"

    async def test_returns_404_when_document_not_found(self, client):
        """
        The service returns None when no document matches the ID.
        The route handler checks for None and raises HTTPException(404).
        """
        with patch("app.services.document_service.get_document_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None  # document not found
            response = await client.get("/v1/documents/nonexistent")

        assert response.status_code == 404


class TestUploadDocumentRoute:
    async def test_returns_201_on_valid_txt_upload(self, client, sample_indexing_response):
        """
        Happy path: upload a .txt file → text is extracted → service indexes it → 201 returned.

        We let extract_text run for real (it just decodes bytes for .txt — no external calls).
        We only mock index_document to avoid hitting OpenAI and the database.
        """
        with patch("app.services.document_service.index_document", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = sample_indexing_response
            response = await client.post(
                "/v1/documents/upload",
                files={"file": ("report.txt", b"Annual report content goes here.", "text/plain")},
                data={"title": "Annual Report", "source": "hr"},
            )

        assert response.status_code == 201
        assert response.json()["chunk_count"] == 5

    async def test_returns_422_on_unsupported_file_type(self, client):
        """
        If the uploaded file is not .txt/.pdf/.docx, extract_text raises ValueError.
        The route handler catches it and returns 422 — no mocking needed because
        the error is raised before index_document is ever called.
        """
        response = await client.post(
            "/v1/documents/upload",
            files={"file": ("data.csv", b"col1,col2\n1,2", "text/csv")},
        )

        assert response.status_code == 422


class TestDeleteDocumentRoute:
    async def test_returns_204_when_deleted(self, client):
        """
        204 No Content — successful delete with no response body.
        This is the REST convention for DELETE operations.
        """
        with patch("app.services.document_service.delete_document", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True  # rows were deleted
            response = await client.delete("/v1/documents/abc-123")

        assert response.status_code == 204

    async def test_returns_404_when_document_not_found(self, client):
        with patch("app.services.document_service.delete_document", new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = False  # nothing to delete
            response = await client.delete("/v1/documents/nonexistent")

        assert response.status_code == 404