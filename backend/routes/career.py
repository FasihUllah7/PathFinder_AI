from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException

from ..services.storage_service import StorageService
from ..services.career_service import recommend_career
from ..models.responses import RecommendationResponse

router = APIRouter(tags=["career"])

storage = StorageService()


@router.post("/analyze")
async def analyze(user_id: str) -> Dict[str, Any]:
    """Aggregate user's stored context and return a reconstructed profile snapshot."""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    results = storage.query_user(user_id=user_id, query_text="profile summary", top_k=5)
    profile_meta = next((r.get("metadata") or {} for r in results if (r.get("metadata") or {}).get("type") == "profile"), {})
    profile = {
        "user_id": user_id,
        "summary": profile_meta.get("summary", ""),
        "skills": profile_meta.get("skills", []),
        "experience": profile_meta.get("experience", []),
        "education": profile_meta.get("education", []),
    }
    return {"profile": profile, "evidence_count": len(results)}


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(user_id: str, interests: Optional[List[str]] = None):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    # Retrieve user context (only user's docs) and aggregate
    query = "career recommendation " + (" ".join(interests or []))
    results = storage.query_user(user_id=user_id, query_text=query, top_k=5)
    ctx = "\n\n".join([r.get("document") or "" for r in results])

    # Attempt to reconstruct a lightweight profile from top metadata
    profile_meta = next((r.get("metadata") or {} for r in results if (r.get("metadata") or {}).get("type") == "profile"), {})
    profile = {
        "summary": profile_meta.get("summary", ""),
        "skills": profile_meta.get("skills", []),
        "experience": profile_meta.get("experience", []),
        "education": profile_meta.get("education", []),
    }

    rec = recommend_career(profile=profile, interests=interests or [], retrieved_context=ctx)
    return RecommendationResponse(**rec)
