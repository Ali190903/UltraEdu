import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class VariantCreateRequest(BaseModel):
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict  # {"easy": 10, "medium": 10, "hard": 5}
    topic_dist: dict | None = None  # {"topic1": 5, "topic2": 10} or null for auto
    grade: list[int] = [11]

    @field_validator("grade", mode="before")
    @classmethod
    def _wrap_single_grade(cls, v):
        if isinstance(v, int):
            return [v]
        return v

    @model_validator(mode="after")
    def _check_difficulty_sum(self):
        dist_sum = sum(self.difficulty_dist.values())
        if dist_sum != self.total_questions:
            raise ValueError(
                f"difficulty_dist values must sum to total_questions "
                f"({dist_sum} != {self.total_questions})"
            )
        return self


class VariantResponse(BaseModel):
    id: uuid.UUID
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict
    created_at: datetime

    model_config = {"from_attributes": True}