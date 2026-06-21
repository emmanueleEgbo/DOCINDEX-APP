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


class TestQueryRoute:
    async def test_returns_200_with_answer(self, client, valid_body, sample_response):
        with patch("app.services.query_service.query_documents", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = sample_response
            response = await client.post("/v1/query", json=valid_body)

        assert response.status_code == 200
        data = response.json()
        assert data["question"] == "What is the refund policy?"
        assert "refund" in data["answer"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["title"] == "Acme Corp FAQ"