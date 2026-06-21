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