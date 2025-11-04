import os
from typing import List, Optional

import streamlit as st
import requests

DEFAULT_API_BASE = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")


def post_upload_cv(api_base: str, user_id: str, file, text: Optional[str]):
    url = f"{api_base}/user/upload_cv"
    data = {"user_id": user_id}
    files = None
    if file is not None:
        file_bytes = file.getvalue()
        files = {
            "file": (file.name, file_bytes, file.type or "application/octet-stream"),
        }
    if text and text.strip():
        data["text"] = text

    resp = requests.post(url, data=data, files=files, timeout=60)
    resp.raise_for_status()
    return resp.json()


def post_interests(api_base: str, user_id: str, interests: List[str]):
    url = f"{api_base}/user/interests"
    payload = {"user_id": user_id, "interests": interests}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def post_analyze(api_base: str, user_id: str):
    url = f"{api_base}/career/analyze"
    resp = requests.post(url, params={"user_id": user_id}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def post_recommend(api_base: str, user_id: str, interests: List[str]):
    url = f"{api_base}/career/recommend"
    params = {"user_id": user_id}
    # requests will encode list values as repeated query params
    for i in interests:
        params.setdefault("interests", []).append(i)
    resp = requests.post(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


st.set_page_config(page_title="AI Career Guidance", page_icon="🧭", layout="wide")

if "api_base" not in st.session_state:
    st.session_state.api_base = DEFAULT_API_BASE
if "user_id" not in st.session_state:
    st.session_state.user_id = "user-1"

with st.sidebar:
    st.header("Settings")
    st.session_state.api_base = st.text_input("API Base URL", value=st.session_state.api_base, help="FastAPI base URL")
    st.session_state.user_id = st.text_input("User ID", value=st.session_state.user_id)
    st.caption("Ensure the FastAPI server is running.")

st.title("AI Career Guidance 🧭")

tab_upload, tab_interests, tab_analyze, tab_recommend = st.tabs([
    "Upload CV",
    "Set Interests",
    "Analyze",
    "Recommend",
])

with tab_upload:
    st.subheader("Upload your CV")
    uploaded_file = st.file_uploader("Choose a PDF or TXT", type=["pdf", "txt"])
    or_text = st.text_area("Or paste your resume text", height=200)
    if st.button("Upload & Parse", type="primary"):
        if not uploaded_file and not or_text.strip():
            st.warning("Please upload a file or paste text.")
        else:
            with st.spinner("Uploading and parsing CV..."):
                try:
                    resp = post_upload_cv(
                        st.session_state.api_base, st.session_state.user_id, uploaded_file, or_text
                    )
                    st.success("Parsed and stored successfully.")
                    profile = resp.get("profile", {})
                    st.json(profile)
                except requests.HTTPError as e:
                    st.error(f"Upload failed: {e.response.text if e.response is not None else e}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

with tab_interests:
    st.subheader("Your Interests")
    preset = [
        "AI", "Data Science", "Analytics", "Software Engineering", "MLOps", "Cloud", "NLP", "CV",
    ]
    selected = st.multiselect("Pick some interests (optional)", options=preset)
    custom = st.text_input("Add more (comma-separated)")
    interests = selected + [s.strip() for s in custom.split(",") if s.strip()]
    if st.button("Save Interests"):
        if not interests:
            st.info("No interests provided; you can still proceed to Recommend.")
        try:
            with st.spinner("Saving interests..."):
                resp = post_interests(st.session_state.api_base, st.session_state.user_id, interests)
                st.success(f"Saved {resp.get('count', 0)} interests.")
        except requests.HTTPError as e:
            st.error(f"Save failed: {e.response.text if e.response is not None else e}")
        except Exception as e:
            st.error(f"Save failed: {e}")

with tab_analyze:
    st.subheader("Analyze Stored Profile")
    if st.button("Analyze Profile"):
        try:
            with st.spinner("Aggregating your stored profile..."):
                resp = post_analyze(st.session_state.api_base, st.session_state.user_id)
                st.json(resp)
        except requests.HTTPError as e:
            st.error(f"Analyze failed: {e.response.text if e.response is not None else e}")
        except Exception as e:
            st.error(f"Analyze failed: {e}")

with tab_recommend:
    st.subheader("Get Career Recommendation")
    extra = st.text_input("Optional: interests to emphasize (comma-separated)")
    extra_list = [s.strip() for s in extra.split(",") if s.strip()]
    if st.button("Recommend"):
        try:
            with st.spinner("Reasoning about the best path for you..."):
                resp = post_recommend(st.session_state.api_base, st.session_state.user_id, extra_list)
                st.success("Recommendation ready")
                st.markdown(f"### Recommended Career\n**{resp.get('recommended_career','')}**")
                st.markdown("### Why")
                st.write(resp.get("justification", ""))
                st.markdown("### Learning Path")
                for step in resp.get("learning_path", []):
                    st.write(f"- {step}")
                st.markdown("### Next Steps")
                for step in resp.get("next_steps", []):
                    st.write(f"- {step}")
        except requests.HTTPError as e:
            st.error(f"Recommend failed: {e.response.text if e.response is not None else e}")
        except Exception as e:
            st.error(f"Recommend failed: {e}")
