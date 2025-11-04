from typing import List
from pathlib import Path

from .config import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    EMBEDDING_MODEL,
    OPENAI_MODEL,
    CHROMA_DIR,
)

# LangChain / OpenAI
try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
except Exception:  # pragma: no cover - allow import absence during static checks
    OpenAIEmbeddings = None
    ChatOpenAI = None

# Chroma
try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None


class EmbeddingNotConfigured(RuntimeError):
    pass


def _assert_emb_ready():
    if OpenAIEmbeddings is None or chromadb is None:
        raise EmbeddingNotConfigured(
            "Embeddings/Chroma not available. Install dependencies and set OPENAI_API_KEY."
        )
    if not OPENAI_API_KEY:
        raise EmbeddingNotConfigured("OPENAI_API_KEY is not set in environment/.env")


def get_llm():
    _assert_emb_ready()
    return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE, temperature=0.2)


def get_embedder():
    _assert_emb_ready()
    return OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)


_client = None
_collection = None


def get_chroma_client():
    global _client
    _assert_emb_ready()
    if _client is None:
        Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(name="user_profiles")
    return _collection


def embed_texts(texts: List[str]) -> List[List[float]]:
    embedder = get_embedder()
    return embedder.embed_documents(texts)
