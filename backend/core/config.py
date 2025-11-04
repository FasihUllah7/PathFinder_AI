import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Project directories
BACKEND_DIR = Path(__file__).resolve().parents[1]
DATABASE_DIR = BACKEND_DIR / "database"
DEFAULT_CHROMA_DIR = DATABASE_DIR / "chroma"

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")  # Optional (e.g., Azure OpenAI or OpenRouter)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHROMA_DIR = os.getenv("CHROMA_DIR", str(DEFAULT_CHROMA_DIR))

# Service tuning
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
MAX_CTX_CHARS = int(os.getenv("MAX_CTX_CHARS", "12000"))


def ensure_dirs():
    Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

ensure_dirs()
