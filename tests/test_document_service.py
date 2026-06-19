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