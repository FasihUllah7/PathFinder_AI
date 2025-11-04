from typing import List
from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    recommended_career: str
    justification: str
    learning_path: List[str]
    next_steps: List[str]
