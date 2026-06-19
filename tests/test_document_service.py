"""
Unit tests for document_service — the indexing pipeline orchestrator.

The service coordinates three things: chunking, embedding, and the repository.
In these tests, we mock both the embedding API and the repository so we only
test the service's own logic (UUID generation, wiring the steps together,
error propagation) — not the steps themselves.

Mocking strategy:
  - patch("app.services.document_service.embed_batch")
    patches embed_batch AS IT IS IMPORTED inside document_service.
    This is a critical rule: always patch where the name is USED, not where
    it is DEFINED. document_service imports embed_batch, so that's where we patch.

  - patch("app.services.document_service.DocumentRepository")
    patches the entire repository class so no DB call is made.

Mock setup pattern used consistently throughout this file:
    mock_repo = AsyncMock()                        # 1. create the fake instance
    mock_repo.some_method.return_value = result    # 2. tell it what to return
    MockRepo.return_value = mock_repo              # 3. make the class return that instance
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.schemas.document_schema import DocumentCreate, DocumentSummary, IndexingResponse


@pytest.fixture
def sample_create():
    """A valid DocumentCreate input — reused across multiple tests."""
    return DocumentCreate(
        title="Test Doc",
        content="Hello world " * 20,
        source="test",
    )


class TestIndexDocument:
    async def test_returns_indexing_response(self, mock_db, sample_create):
        from app.services import document_service

        with patch("app.services.document_service.embed_batch", new_callable=AsyncMock) as mock_embed, \
             patch("app.services.document_service.DocumentRepository") as MockRepo:

            # embed_batch return value doesn't matter — it is passed straight into
            # the mocked create_chunks which ignores its arguments entirely.
            # We still need the mock so the real OpenAI call is never made.
            mock_embed.return_value = []

            mock_repo = AsyncMock()
            mock_repo.create_chunks.return_value = [None] * 5 
            MockRepo.return_value = mock_repo

            result = await document_service.index_document(mock_db, sample_create)

        assert isinstance(result, IndexingResponse)
        assert result.title == "Test Doc"
        assert result.chunk_count >= 1


    async def test_source_document_id_is_a_uuid_string(self, mock_db, sample_create):
        """
        The service generates a UUID for each document. Verify it's a valid UUID
        by trying to parse it — uuid.UUID() raises ValueError if the format is wrong.
        """
        from app.services import document_service

        with patch("app.services.document_service.embed_batch", new_callable=AsyncMock) as mock_embed, \
             patch("app.services.document_service.DocumentRepository") as MockRepo:

            mock_embed.return_value = []

            mock_repo = AsyncMock()
            mock_repo.create_chunks.return_value = [None] * 5
            MockRepo.return_value = mock_repo

            result = await document_service.index_document(mock_db, sample_create)

        # uuid.UUID() raises ValueError if source_document_id is not a valid UUID format
        uuid.UUID(result.source_document_id)


class TestGetAllDocuments:
    async def test_returns_list_from_repository(self, mock_db, sample_summary):
        from app.services import document_service

        with patch("app.services.document_service.DocumentRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_document_summaries.return_value = [sample_summary]
            MockRepo.return_value = mock_repo

            result = await document_service.get_all_documents(mock_db)

        assert len(result) == 1
        assert result[0].title == "Test Doc"

    async def test_returns_empty_list_when_no_documents(self, mock_db):
        from app.services import document_service

        with patch("app.services.document_service.DocumentRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_document_summaries.return_value = []
            MockRepo.return_value = mock_repo

            result = await document_service.get_all_documents(mock_db)

        assert result == []