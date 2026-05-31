"""
Pydantic schemas define the shape of data in and out of the API.

Three clear separations:
  - DocumentCreate:   what the client sends in the request body
  - ChunkResponse:    one chunk row (no embedding — it's huge and not useful to clients)
  - DocumentResponse: summary of a full document (groups chunks)
  - DocumentDetail:   one document's metadata + its chunk count
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime