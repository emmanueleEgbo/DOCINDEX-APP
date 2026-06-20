"""
Unit tests for embedding_service.

These tests mock the OpenAI API client so no real API calls are made.
This is important for three reasons:
  1. Tests must be fast and deterministic — a real API call is slow and can fail
  2. We don't want to pay for API calls during testing
  3. We want to control exactly what the API "returns" to test edge cases

Key mocking tools used:
  - patch.object(target, attribute)  : temporarily replace one attribute on an object
  - AsyncMock                        : a mock that is awaitable (needed for async functions)
  - MagicMock                        : a mock for regular (non-async) objects and attributes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def make_openai_response(n: int, value: float = 0.1):
    """
    Build a fake OpenAI embeddings API response.

    The real OpenAI response looks like:
        response.data = [
            Embedding(index=0, embedding=[0.1, 0.2, ...]),
            Embedding(index=1, embedding=[0.3, 0.4, ...]),
        ]

    MagicMock() creates an object that accepts any attribute access or method call,
    making it easy to fake complex nested objects like API responses.
    """
    response = MagicMock()
    response.data = [
        MagicMock(index=i, embedding=[value] * 1536)
        for i in range(n)
    ]
    return response


class TestEmbedBatch:
    async def test_empty_input_returns_empty_list(self):
        from app.services.embedding_service import embed_batch
        # embed_batch has an early return for empty input — no API call made
        result = await embed_batch([])
        assert result == []

    async def test_returns_one_vector_per_text(self):
        from app.services.embedding_service import embed_batch, _client

        texts = ["chunk one", "chunk two", "chunk three"]

        # patch.object(target, attribute) temporarily replaces _client.embeddings.create
        # with an AsyncMock for the duration of the `with` block.
        # After the block exits, the real method is restored automatically.
        # This is equivalent to Django's @mock.patch decorator but used as a context manager.
        with patch.object(_client.embeddings, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = make_openai_response(3)
            result = await embed_batch(texts)

        assert len(result) == 3

    async def test_each_vector_has_1536_dimensions(self):
        from app.services.embedding_service import embed_batch, _client

        with patch.object(_client.embeddings, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = make_openai_response(2)
            result = await embed_batch(["text a", "text b"])

        assert all(len(vec) == 1536 for vec in result)

    async def test_api_error_raises_runtime_error(self):
        from app.services.embedding_service import embed_batch, _client

        # side_effect makes the mock raise an exception when called,
        # simulating an OpenAI API failure (timeout, rate limit, etc.)
        with patch.object(_client.embeddings, "create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API timeout")
            with pytest.raises(RuntimeError, match="Embedding API failed"):
                await embed_batch(["some text"])

    async def test_output_order_matches_input_order(self):
        """
        The OpenAI API guarantees order via the `index` field, not by the order
        returned in the response. embed_batch() sorts by index explicitly.
        This test verifies that sorting works correctly.
        """
        from app.services.embedding_service import embed_batch, _client

        # Return embeddings in reverse index order to simulate out-of-order API response
        response = MagicMock()
        response.data = [
            MagicMock(index=2, embedding=[0.3] * 1536),  # last item returned first
            MagicMock(index=0, embedding=[0.1] * 1536),  # first item returned second
            MagicMock(index=1, embedding=[0.2] * 1536),  # middle item returned last
        ]
        with patch.object(_client.embeddings, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = response
            result = await embed_batch(["a", "b", "c"])

        # After sorting by index, order should be: 0.1, 0.2, 0.3
        # pytest.approx() handles floating point comparison safely
        assert pytest.approx(result[0][0]) == 0.1  # index 0
        assert pytest.approx(result[1][0]) == 0.2  # index 1
        assert pytest.approx(result[2][0]) == 0.3  # index 2
