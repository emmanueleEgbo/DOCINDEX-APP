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


async def extract_text(file: UploadFile) -> str:
    """
    Read the uploaded file and return its text content as a plain string.
    Raises ValueError for unsupported file types.
    """
    filename = (file.filename or "").lower()
    content = await file.read()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    
    elif filename.endswith(".pdf"):
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    
    elif filename.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(
            para.text for para in doc.paragraphs if para.text.strip()
        )
    
    else:
        raise ValueError(
            f"Unsupported file type '{filename}'. Supported formats: .txt, .pdf, .docx"
        )