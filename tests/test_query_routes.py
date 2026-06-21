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