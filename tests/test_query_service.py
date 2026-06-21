"""
Unit tests for query_service — the retrieval pipeline orchestrator.

Mocks:
  - embed_text      → avoid real OpenAI embedding call
  - DocumentRepository → avoid real DB query
  - generate_answer → avoid real LLM call
"""