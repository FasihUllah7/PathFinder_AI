import io
import json
from typing import Dict, Any

from ..core.utils import clean_text
from ..core.embeddings import get_llm

# PDF parsing
try:
    import PyPDF2
except Exception:  # pragma: no cover
    PyPDF2 = None


def extract_text_from_pdf_bytes(data: bytes) -> str:
    if PyPDF2 is None:
        raise RuntimeError("PyPDF2 is not installed; cannot parse PDF.")
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    contents = []
    for page in reader.pages:
        try:
            contents.append(page.extract_text() or "")
        except Exception:
            continue
    return clean_text("\n".join(contents))


def parse_profile_from_text(text: str) -> Dict[str, Any]:
    """Summarize CV text and extract structured fields using LLM; returns dict.
    Fallback: lightweight heuristics when LLM is unavailable.
    """
    text = clean_text(text)
    try:
        llm = get_llm()
    except Exception:
        # Fallback heuristics
        skills = []
        for token in set([t.strip(',.;:') for t in text.split()]):
            if token.lower() in {"python", "sql", "excel", "ml", "nlp", "java", "c++", "javascript", "pandas", "numpy"}:
                skills.append(token)
        return {
            "summary": text[:500] + ("..." if len(text) > 500 else ""),
            "skills": sorted(list(set(skills)))[:20],
            "experience": [],
            "education": [],
        }

    system = (
        "You are an expert career analyst. Read the user's CV/resume text and extract a JSON with keys:"
        " summary (2-3 sentences), skills (array of concise skill names), experience (array of role highlights),"
        " education (array of degree/program entries). Return ONLY valid JSON."
    )
    user = f"CV Text:\n{text[:12000]}"
    msg = llm.invoke([
        ("system", system),
        ("user", user),
    ])
    content = getattr(msg, "content", "") if msg else ""
    try:
        data = json.loads(content)
    except Exception:
        # Try to locate JSON in content
        start = content.find("{")
        end = content.rfind("}")
        data = json.loads(content[start : end + 1]) if start != -1 and end != -1 else {
            "summary": text[:500] + ("..." if len(text) > 500 else ""),
            "skills": [],
            "experience": [],
            "education": [],
        }
    # Ensure shapes
    data.setdefault("summary", "")
    data.setdefault("skills", [])
    data.setdefault("experience", [])
    data.setdefault("education", [])
    return data
