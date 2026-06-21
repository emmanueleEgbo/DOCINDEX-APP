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