from typing import Dict, List, Optional, Any

from ..core.embeddings import get_collection, embed_texts


class StorageService:
    """ChromaDB storage and retrieval wrapper for user context."""

    def __init__(self):
        self.collection = get_collection()

    def _sanitize_metadata(self, meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Chroma metadata must be primitives; coerce lists/dicts/others to strings."""
        if not meta:
            return {}
        clean: Dict[str, Any] = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                clean[k] = v
            elif isinstance(v, list):
                try:
                    clean[k] = ", ".join(map(str, v))
                except Exception:
                    clean[k] = str(v)
            elif isinstance(v, dict):
                # Flatten one level by stringifying
                clean[k] = "; ".join(f"{kk}={vv}" for kk, vv in v.items())
            else:
                clean[k] = str(v)
        return clean

    def add_user_doc(self, user_id: str, text: str, metadata: Dict):
        # Ensure user_id in metadata for filtering
        meta = dict(metadata or {})
        meta.setdefault("user_id", user_id)
        emb = embed_texts([text])[0]
        doc_id = meta.get("id") or f"{user_id}:{meta.get('type','doc')}"
        safe_meta = self._sanitize_metadata(meta)
        self.collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[safe_meta],
            embeddings=[emb],
        )
        return doc_id

    def query_user(self, user_id: str, query_text: str, top_k: int = 5) -> List[Dict]:
        q_emb = embed_texts([query_text])[0]
        res = self.collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            where={"user_id": user_id},
        )
        # Normalize result into list of dicts
        results: List[Dict] = []
        for i in range(len(res.get("ids", [[]])[0])):
            results.append(
                {
                    "id": res["ids"][0][i],
                    "document": res.get("documents", [[None]])[0][i],
                    "metadata": res.get("metadatas", [[None]])[0][i],
                    "distance": res.get("distances", [[None]])[0][i],
                }
            )
        return results
