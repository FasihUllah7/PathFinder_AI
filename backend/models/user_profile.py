from typing import List, Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: str
    summary: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    interests: Optional[List[str]] = None


class InterestsRequest(BaseModel):
    user_id: str
    interests: List[str]


class CVUploadResponse(BaseModel):
    user_id: str
    profile: UserProfile
