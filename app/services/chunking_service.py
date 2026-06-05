"""
Fixed-size chunking with overlap.

Chunking is character-based here for simplicity.
  1 token ≈ 4 characters (English text).
  chunk_size=500 tokens → 500 × 4 = 2,000 characters per chunk.
  chunk_overlap=50 tokens → 50 × 4 = 200 characters of overlap.
"""