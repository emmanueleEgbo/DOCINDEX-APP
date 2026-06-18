"""
Unit tests for chunking_service.

clean_text() and chunk_text() are plain functions with no external dependencies
(no database, no HTTP calls, no OpenAI). So we just call them directly and
assert on the output.

We group tests into classes purely for organisation — unlike Django's TestCase,
these classes do NOT need to inherit from anything. pytest discovers and runs
any function starting with `test_` inside any class starting with `Test`.
"""