from __future__ import annotations
import logging
from typing import List
import re
from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("app")


# ============================================================
#       Try to import NLTK and ensure required models exist
# ============================================================
try:
    import nltk

    # Automatically download required resources if not found
    for resource in ["punkt", "punkt_tab"]:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)

    from nltk.tokenize import sent_tokenize

    NLTK_AVAILABLE = True
except Exception:
    # NLTK not available or resource download failed
    NLTK_AVAILABLE = False


# ============================================================
#                    Public main function
# ============================================================


def split_text_semantic(
    text: str, chunk_size: int = 800, overlap: int = 150, recursive: bool = True
) -> List[str]:
    """
    Main entrypoint for splitting text into semantically meaningful chunks.
    The function combines paragraph splitting, sentence grouping, and overlap.

    Args:
        text (str): Input text to split.
        chunk_size (int): Approximate number of characters per chunk.
        overlap (int): Overlap between consecutive chunks (in characters).
        recursive (bool): Whether to recursively split long chunks.

    Returns:
        List[str]: List of processed text chunks.
    """
    # Normalize input
    text = _normalize_text(text)

    # Split into paragraphs
    paragraphs = _split_into_paragraphs(text)

    # Convert paragraphs to chunks (sentence-aware)
    chunks = _split_paragraphs_into_chunks(paragraphs, chunk_size)

    # Optionally apply recursive splitting
    if recursive:
        chunks = _apply_recursive_split(chunks, chunk_size, overlap)

    # Add overlap between chunks for continuity
    chunks = _apply_overlap(chunks, overlap)

    return [c.strip() for c in chunks if c.strip()]


# ============================================================
#                       Internal helpers
# ============================================================


def _normalize_text(text: str) -> str:
    """Cleans carriage returns, extra spaces, and trims the text."""
    return text.strip().replace("\r", "")


def _split_into_paragraphs(text: str) -> List[str]:
    """
    Splits text by double newlines or multiple line breaks,
    preserving logical paragraph boundaries.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paragraphs


def _split_paragraphs_into_chunks(paragraphs: List[str], chunk_size: int) -> List[str]:
    """
    Converts paragraphs into manageable chunks using sentence boundaries.
    Falls back to regex-based sentence splitting if NLTK is unavailable.
    """
    chunks = []
    for para in paragraphs:
        sentences = _split_into_sentences(para)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())
    return chunks


def _split_into_sentences(text: str) -> List[str]:
    """Splits a paragraph into sentences using NLTK or a simple regex fallback."""
    if NLTK_AVAILABLE:
        return sent_tokenize(text)
    # Fallback: split by punctuation followed by space or linebreak
    return re.split(r"(?<=[.!?])\s+", text)


def _apply_recursive_split(
    chunks: List[str], chunk_size: int, overlap: int
) -> List[str]:
    """
    Recursively splits overly large chunks using raw length-based splitting.
    """
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size * 1.5:
            sub_chunks = _split_by_length(chunk, chunk_size, overlap)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)
    return final_chunks


def _split_by_length(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Fallback raw splitter for extremely long text segments.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def _apply_overlap(chunks: List[str], overlap: int) -> List[str]:
    """
    Applies overlap between consecutive chunks for contextual continuity.
    """
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_chunk = overlapped[-1]
        new_chunk = prev_chunk[-overlap:] + " " + chunks[i]
        overlapped.append(new_chunk)
    return overlapped
