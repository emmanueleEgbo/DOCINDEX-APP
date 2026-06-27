"""
Unit tests for Pydantic request/response schemas.

Pydantic models validate data at instantiation time — if the data is invalid,
they raise a ValidationError immediately. These tests just instantiate the
models with different inputs and check the outcome.

No mocking, no HTTP calls, no database — pure data validation tests.
"""
import pytest
from pydantic import ValidationError
from app.schemas.document_schema import DocumentCreate


class TestDocumentCreate:
    def test_valid_full_document(self):
        # all fields valid, model should instantiate without error
        doc = DocumentCreate(title="Test", content="Some content here", source="faq")
        assert doc.title == "Test"
        assert doc.content == "Some content here"
        assert doc.source == "faq"

    def test_source_is_optional_defaults_to_none(self):
        # `source` has a default of None in the schema, so omitting it is valid
        doc = DocumentCreate(title="Test", content="Some content here")
        assert doc.source is None

    def test_empty_content_raises_validation_error(self):
        # The @field_validator("content") in the schema rejects empty strings.
        # ValidationError is Pydantic's equivalent of Django's ValidationError.
        with pytest.raises(ValidationError):
            DocumentCreate(title="Test", content="")

    def test_empty_title_raises_validation_error(self):
        with pytest.raises(ValidationError):
            DocumentCreate(title="", content="Some content")