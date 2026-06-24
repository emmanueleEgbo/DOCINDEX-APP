"""
Unit tests for query_service — the retrieval pipeline orchestrator.

Mocks:
  - embed_text      → avoid real OpenAI embedding call
  - DocumentRepository → avoid real DB query
  - generate_answer → avoid real LLM call
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.schemas.query_schema import QueryRequest, QueryResponse

@pytest.fixture
def sample_request():
    return QueryRequest(question="What is the refund policy?", top_k=5)


@pytest.fixture
def sample_rows():
    """Fake DB rows — mimics what search_similar_chunks returns."""
    row = MagicMock()
    row.title = "Acme Corp FAQ"
    row.source = "faq"
    row.content = "We offer a 30-day full refund on all purchases."
    row.similarity = 0.94
    return [row]


class TestQueryDocuments:
    async def test_returns_query_response(self, mock_db, sample_request, sample_rows):
        from app.services import query_service

        with patch("app.services.query_service.embed_text", new_callable=AsyncMock) as mock_embed, \
            patch("app.services.query_service.DocumentRepository") as MockRepo, \
            patch("app.services.query_service.generate_answer", new_callable=AsyncMock) as mock_llm:
            
            mock_embed.return_value = [0.1] * 1536

            mock_repo = AsyncMock()
            mock_repo.search_similar_chunks.return_value = sample_rows
            MockRepo.return_value = mock_repo

            mock_llm.return_value = "We offer a 30-day full refund on all purchases."

            result = await query_service.query_documents(mock_db, sample_request)

        assert isinstance(result, QueryResponse)
        assert result.answer == "We offer a 30-day full refund on all purchases."
        assert len(result.sources) == 1
        assert result.sources[0].title == "Acme Corp FAQ"
    async def test_returns_early_when_no_chunks_found(self, mock_db, sample_request):
        """If pgvector finds no matching chunks, return a canned response immediately."""
        from app.services import query_service

        with patch("app.services.query_service.embed_text", new_callable=AsyncMock) as mock_embed, \
             patch("app.services.query_service.DocumentRepository") as MockRepo, \
             patch("app.services.query_service.generate_answer", new_callable=AsyncMock) as mock_llm:

            mock_embed.return_value = [0.1] * 1536

            mock_repo = AsyncMock()
            mock_repo.search_similar_chunks.return_value = []  # nothing in the DB
            MockRepo.return_value = mock_repo

            result = await query_service.query_documents(mock_db, sample_request)

        # LLM should never be called if there are no chunks to pass as context
        mock_llm.assert_not_called()
        assert result.sources == []
        assert "don't have enough information" in result.answer
    
    async def test_similarity_score_is_rounded(self, mock_db, sample_request, sample_rows):
        """Similarity is rounded to 4 decimal places before returning."""

        from app.services import query_service

        sample_rows[0].similarity = 0.938271828
