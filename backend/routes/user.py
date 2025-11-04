from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from ..services.profile_service import extract_text_from_pdf_bytes, parse_profile_from_text
from ..services.storage_service import StorageService
from ..models.user_profile import UserProfile, InterestsRequest, CVUploadResponse
from ..core.utils import clean_text

router = APIRouter(tags=["user"])

storage = StorageService()


@router.post("/upload_cv", response_model=CVUploadResponse)
async def upload_cv(
    user_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a file or text content")

    content = ""
    if file is not None:
        data = await file.read()
        if file.content_type and "pdf" in file.content_type.lower():
            content = extract_text_from_pdf_bytes(data)
        else:
            try:
                content = data.decode("utf-8", errors="ignore")
            except Exception:
                content = ""
    else:
        content = text or ""

    content = clean_text(content)
    if not content:
        raise HTTPException(status_code=400, detail="No parsable content provided")

    parsed = parse_profile_from_text(content)

    # Compose a profile text for embedding
    profile_text = (
        f"SUMMARY: {parsed.get('summary','')}\n"
        f"SKILLS: {', '.join(parsed.get('skills', []))}\n"
        f"EXPERIENCE: {' | '.join(parsed.get('experience', []))}\n"
        f"EDUCATION: {' | '.join(parsed.get('education', []))}"
    )

    # Store raw CV and structured profile
    storage.add_user_doc(user_id, content, {"type": "cv_raw", "user_id": user_id})
    storage.add_user_doc(
        user_id,
        profile_text,
        {
            "type": "profile",
            "user_id": user_id,
            "summary": parsed.get("summary", ""),
            "skills": parsed.get("skills", []),
            "experience": parsed.get("experience", []),
            "education": parsed.get("education", []),
        },
    )

    profile = UserProfile(
        user_id=user_id,
        summary=parsed.get("summary", ""),
        skills=parsed.get("skills", []),
        experience=parsed.get("experience", []),
        education=parsed.get("education", []),
        interests=None,
    )
    return CVUploadResponse(user_id=user_id, profile=profile)


@router.post("/interests")
async def set_interests(req: InterestsRequest):
    # Store interests as a document for retrieval context
    text = f"INTERESTS: {', '.join(req.interests)}"
    storage.add_user_doc(
        req.user_id,
        text,
        {"type": "interests", "user_id": req.user_id, "interests": req.interests},
    )
    return {"status": "ok", "user_id": req.user_id, "count": len(req.interests)}
