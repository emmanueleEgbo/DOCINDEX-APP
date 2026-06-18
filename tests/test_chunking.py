"""
Unit tests for chunking_service.

clean_text() and chunk_text() are plain functions with no external dependencies
(no database, no HTTP calls, no OpenAI). So we just call them directly and
assert on the output.

We group tests into classes purely for organisation — unlike Django's TestCase,
these classes do NOT need to inherit from anything. pytest discovers and runs
any function starting with `test_` inside any class starting with `Test`.
"""
import pytest
from app.services.chunking_service import clean_text, chunk_text


class TestCleanText:
    def test_collapses_multiple_spaces(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        assert clean_text("line1\nline2\n\nline3") == "line1 line2 line3"

    def test_collapses_tabs(self):
        assert clean_text("col1\tcol2") == "col1 col2"

    def test_strips_leading_and_trailing_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_removes_null_byte(self):
        assert clean_text("hello\x00world") == "helloworld"

    def test_empty_string_returns_empty(self):
        assert clean_text("") == ""


class TestChunkText:
    def test_short_text_produces_one_chunk(self):
        chunks = chunk_text("short text", chunk_size=50, overlap=5)
        assert len(chunks) == 1
        assert chunks[0] == "short text"

    def test_long_text_produces_multiple_chunks(self):
        # chunk_size=10 tokens × 4 chars/token = 40 chars per chunk
        # 200 chars of text should produce more than one chunk
        chunks = chunk_text("a" * 200, chunk_size=10, overlap=2)
        assert len(chunks) > 1

    def test_no_chunk_exceeds_max_size(self):
        chunks = chunk_text("a" * 400, chunk_size=10, overlap=2)
        max_chars = 10 * 4  # 40 characters
        for chunk in chunks:
            assert len(chunk) <= max_chars