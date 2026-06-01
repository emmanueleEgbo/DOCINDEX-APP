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

class DocumentCreate(BaseModel):
    """
    What client send when uploading a document.
    """
    title: str
    content: str
    source: Optional[str] = None   # e.g. "faq", "support", "product_manual"

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Nexora Refund Policy",
                "content": "Refunds are processed within 14 business days of the request...",
                "source": "support_docs"
            }
        }
    }
