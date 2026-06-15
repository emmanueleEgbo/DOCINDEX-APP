"""
Extracts plain text from uploaded files.

Supported formats:
  .txt  — read directly
  .pdf  — extracted page by page using PyMuPDF
  .docx — extracted paragraph by paragraph using python-docx

The extracted text is passed straight into the existing indexing pipeline
(chunking → embedding → store) — no other changes needed.
"""
import io
from fastapi import UploadFile
