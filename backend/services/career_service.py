import json
from typing import Dict, Any, List

from ..core.embeddings import get_llm
from ..core.utils import clean_text


def recommend_career(profile: Dict[str, Any], interests: List[str], retrieved_context: str) -> Dict[str, Any]:
    """Use LLM to recommend a career + plan. Fallback to simple rules if LLM unavailable."""
    interests = interests or []
    profile = profile or {"summary": "", "skills": [], "experience": [], "education": []}

    # Fallback rule-based recommendation if LLM unavailable
    try:
        llm = get_llm()
    except Exception:
        skills = set([s.lower() for s in profile.get("skills", [])])
        rec = "Data Analyst" if any(k in skills for k in ["sql", "excel"]) else (
            "Data Scientist" if any(k in skills for k in ["python", "ml", "pandas"]) else (
                "Software Engineer" if any(k in skills for k in ["java", "c++", "javascript", "python"]) else "Explore Options"
            )
        )
        plan = [
            "Clarify target roles and domains",
            "Close key skill gaps via curated courses",
            "Build one portfolio project aligned with role",
            "Network and apply to 5-10 roles/week",
        ]
        return {
            "recommended_career": rec,
            "justification": "Rule-based suggestion using detected skills and interests.",
            "learning_path": plan,
            "next_steps": ["Draft a tailored resume", "Update LinkedIn", "Schedule mock interviews"],
        }

    # LLM-powered path
    sys = (
        "You are a senior career coach. Given a user's profile, interests, and retrieved context, recommend a career path and a concrete plan."
        " Respond only with strict JSON keys: recommended_career (string), justification (string),"
        " learning_path (array of strings), next_steps (array of strings)."
    )
    user = (
        f"Profile summary: {profile.get('summary','')}\n"
        f"Skills: {', '.join(profile.get('skills', []))}\n"
        f"Interests: {', '.join(interests)}\n"
        f"Retrieved context (from user's history/embeddings):\n{clean_text(retrieved_context)[:12000]}\n"
        "Return ONLY JSON."
    )
    msg = llm.invoke([("system", sys), ("user", user)])
    content = getattr(msg, "content", "") if msg else ""
    try:
        data = json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        data = json.loads(content[start : end + 1]) if start != -1 and end != -1 else {
            "recommended_career": "Explore Options",
            "justification": "Could not parse model output; provided a safe default.",
            "learning_path": [],
            "next_steps": [],
        }
    # Ensure shapes
    data.setdefault("recommended_career", "Explore Options")
    data.setdefault("justification", "")
    data.setdefault("learning_path", [])
    data.setdefault("next_steps", [])
    return data
