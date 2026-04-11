import uuid
from datetime import datetime
from pydantic import BaseModel


class VariantCreateRequest(BaseModel):
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict  # {"easy": 10, "medium": 10, "hard": 5}
    topic_dist: dict | None = None  # {"topic1": 5, "topic2": 10} or null for auto
    grade: int = 9


class VariantResponse(BaseModel):
    id: uuid.UUID
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict
    created_at: datetime

    model_config = {"from_attributes": True}