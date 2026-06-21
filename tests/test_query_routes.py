"""
Route tests for POST /v1/query.
The query_service is mocked — no DB, no OpenAI calls made.
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.schemas.query_schema import QueryResponse, SourceChunk


@pytest.fixture
def valid_body():
    return {"question": "What is the refund policy?"}


@pytest.fixture
def sample_response():
    return QueryResponse(
        question="What is the refund policy?",
        answer="We offer a 30-day full refund on all purchases.",
        sources=[
            SourceChunk(
                title="Acme Corp FAQ",
                source="faq",
                content="We offer a 30-day full refund on all purchases.",
                similarity=0.94,
            )
        ],
    )
