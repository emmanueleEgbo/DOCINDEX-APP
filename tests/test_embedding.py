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