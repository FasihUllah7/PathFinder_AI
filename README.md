# AI Career Guidance Backend

FastAPI backend that parses user CVs, stores embeddings in ChromaDB, and uses LangChain + GPT for personalized career recommendations.

## Features
- Upload a CV (PDF/text) and extract structured profile (summary, skills, experience, education)
- Store user context as embeddings in ChromaDB for long-term personalization
- Recommend career paths using semantic reasoning (LangChain + GPT)
- Return a structured plan:

```
{
  "recommended_career": "Data Scientist",
  "justification": "Based on your background in analytics and Python...",
  "learning_path": ["Learn ML algorithms", "Build portfolio project on AI"],
  "next_steps": ["Apply for internships in analytics firms"]
}
```

## Project Structure
```
backend/
  main.py
  core/
    config.py
    utils.py
    embeddings.py
  services/
    profile_service.py
    career_service.py
    storage_service.py
  routes/
    career.py
    user.py
  models/
    user_profile.py
    responses.py
  database/
    chroma/   # persistent vector store
.env
requirements.txt
README.md
```

## Configuration
Set environment variables in `.env`:

- `OPENAI_API_KEY` – your OpenAI (or provider-compatible) API key
- `OPENAI_API_BASE` – optional base URL (e.g., Azure OpenAI, OpenRouter)
- `OPENAI_MODEL` – chat model (default: `gpt-4o-mini`)
- `EMBEDDING_MODEL` – embedding model (default: `text-embedding-3-small`)
- `CHROMA_DIR` – persistence directory for Chroma (default points to `backend/database/chroma`)

## Run (local)
> Note: You asked not to install dependencies or create a venv in this session. The commands below are reference-only for when you're ready to run.

```powershell
# Optional: create and activate a virtual environment
# python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install dependencies
# pip install -r requirements.txt

# Run the API (from repo root)
# uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend (Streamlit)
An optional Streamlit UI is available at `frontend/streamlit_app.py` to:
- Upload CVs
- Set interests
- Inspect the aggregated profile
- Request career recommendations

Reference run (when ready):

```powershell
# Ensure the API is running (see above)

# Optionally set a custom API base URL for the UI
# $env:API_BASE_URL = "http://127.0.0.1:8000"

# Launch Streamlit from repo root
# streamlit run frontend/streamlit_app.py
```

## API Endpoints
- `POST /user/upload_cv` (multipart/form-data)
  - fields: `user_id` (form), `file` (UploadFile pdf/txt) or `text` (form)
  - returns: structured profile and persists embeddings

- `POST /user/interests` (application/json)
  - body: `{ "user_id": "u1", "interests": ["AI", "Data Science"] }`
  - stores interests in vector store for personalization

- `POST /career/recommend`
  - query params: `user_id`, optional repeated `interests`
  - uses retrieved user context + interests to generate a personalized plan

## Notes
- Without `OPENAI_API_KEY` and the Python packages installed, the LLM paths are replaced by simple fallbacks for profile parsing and recommendations.
- ChromaDB persists to `backend/database/chroma` by default; delete this folder to reset the index.
- Keep PDFs text-based for best parsing (images-only PDFs need OCR, which is not included here).
