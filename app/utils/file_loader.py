from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Optional
import mimetypes

# Optional dependencies
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import fitz

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import docx

    PYDOCX_AVAILABLE = True
except ImportError:
    PYDOCX_AVAILABLE = False


# ============================================================
#                     Public main function
# ============================================================


def load_text(source: str) -> str:
    """
    Loads and extracts raw text from a file path or URL.

    Args:
        source (str): Local file path or HTTP/HTTPS URL.

    Returns:
        str: Extracted text content.
    """
    if _is_url(source):
        return _load_from_url(source)

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    mime_type, _ = mimetypes.guess_type(path.name)

    if path.suffix.lower() in [".txt", ".md"] or (mime_type and "text" in mime_type):
        return _load_text_file(path)
    elif path.suffix.lower() == ".pdf":
        return _load_pdf_file(path)
    elif path.suffix.lower() in [".docx", ".doc"]:
        return _load_docx_file(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


# ============================================================
#                   Loaders by file type
# ============================================================


def _load_text_file(path: Path) -> str:
    """Reads raw text content from .txt or .md files."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _load_pdf_file(path: Path) -> str:
    """Extracts text from a PDF using PyMuPDF (fitz)."""
    if not PYMUPDF_AVAILABLE:
        raise ImportError(
            "PyMuPDF is required to extract text from PDFs. Run: pip install pymupdf"
        )

    text = ""
    with fitz.open(path) as pdf:
        for page in pdf:
            text += page.get_text("text") + "\n"
    return _normalize_text(text)


def _load_docx_file(path: Path) -> str:
    """Extracts text from a Word (.docx) document."""
    if not PYDOCX_AVAILABLE:
        raise ImportError(
            "python-docx is required for DOCX files. Run: pip install python-docx"
        )

    doc = docx.Document(path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return _normalize_text(text)


def _load_from_url(url: str) -> str:
    """Fetches raw text from a remote URL."""
    if not REQUESTS_AVAILABLE:
        raise ImportError(
            "Requests library required for URL loading. Run: pip install requests"
        )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")

    if "text" in content_type:
        return response.text
    elif "pdf" in content_type:
        # Save temporary PDF and extract text
        tmp_path = Path("temp_download.pdf")
        with open(tmp_path, "wb") as f:
            f.write(response.content)
        text = _load_pdf_file(tmp_path)
        tmp_path.unlink(missing_ok=True)
        return text
    else:
        raise ValueError(f"Unsupported content type from URL: {content_type}")


# ============================================================
#                        Helpers
# ============================================================


def _is_url(source: str) -> bool:
    """Checks whether the given string is an HTTP/HTTPS URL."""
    return source.startswith("http://") or source.startswith("https://")


def _normalize_text(text: str) -> str:
    """Cleans whitespace, removes control characters, and normalizes spacing."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
