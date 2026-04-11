import uuid
from datetime import datetime
from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: uuid.UUID
    subject: str
    grade: int
    topic: str
    subtopic: str | None
    question_type: str
    difficulty: str
    bloom_level: str
    question_text: str
    options: dict | None
    matching_pairs: dict | None
    correct_answer: str
    explanation: str
    latex_content: str | None
    source_reference: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    options: dict | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    status: str | None = None


class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int