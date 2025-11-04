from typing import Iterable, List
import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    # Normalize whitespace and strip control chars
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 3000) -> List[str]:
    text = text or ""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks if chunks else [text]
