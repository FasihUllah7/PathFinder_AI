from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.user import router as user_router
from .routes.career import router as career_router

app = FastAPI(title="AI Career Guidance API", version="0.1.0")

# Allow local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "career-guidance", "version": app.version}

app.include_router(user_router, prefix="/user")
app.include_router(career_router, prefix="/career")
