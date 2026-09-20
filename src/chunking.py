from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Lookbehind splits *after* the punctuation, so ". " / "! " / "? " / ".\n" keep their mark.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip())]
        sentences = [s for s in sentences if s]

        n = self.max_sentences_per_chunk
        return [" ".join(sentences[i : i + n]) for i in range(0, len(sentences), n)]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case 1: already small enough.
        if len(current_text) <= self.chunk_size:
            stripped = current_text.strip()
            return [stripped] if stripped else []

        # Base case 2/3: no separators left, or the "" separator -> hard cut by size.
        if not remaining_separators or remaining_separators[0] == "":
            size = self.chunk_size
            cuts = (current_text[i : i + size].strip() for i in range(0, len(current_text), size))
            return [c for c in cuts if c]

        separator, rest = remaining_separators[0], remaining_separators[1:]
        parts = current_text.split(separator)
        # Keep the separator attached to the piece before it so no text is lost.
        pieces = [p + separator for p in parts[:-1]] + [parts[-1]]

        # Recurse down: any piece still too long is split with the finer separators.
        small: list[str] = []
        for piece in pieces:
            if len(piece) <= self.chunk_size:
                small.append(piece)
            else:
                small.extend(self._split(piece, rest))

        # Merge up: glue adjacent small pieces until just under chunk_size.
        chunks: list[str] = []
        buffer = ""
        for piece in small:
            if buffer and len(buffer) + len(piece) > self.chunk_size:
                chunks.append(buffer.strip())
                buffer = ""
            buffer += piece
        if buffer.strip():
            chunks.append(buffer.strip())
        return [c for c in chunks if c]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        chunkers = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result: dict = {}
        for name, chunker in chunkers.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count else 0.0
            result[name] = {"count": count, "avg_length": avg_length, "chunks": chunks}
        return result
