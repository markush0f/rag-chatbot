"""
similarity.py
-------------
Utility functions for vector similarity computations.
"""

from typing import List


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
