"""
OpenAI embedding API calls.

Two functions:
  embed_text(text)          → embed a single string
  embed_batch(texts)        → embed multiple strings in ONE API call (batch)

Why batch embedding?
  A document split into 20 chunks would require 20 separate API calls if we
  embedded one chunk at a time.
  The OpenAI embedding API accepts a LIST of texts in one call — up to 2,048 items.
  This means: 1 API call regardless of how many chunks we have.
  Faster. Cheaper. Fewer rate limit issues.
"""