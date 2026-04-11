import uuid
from datetime import datetime
from pydantic import BaseModel


class ReportCreateRequest(BaseModel):
    question_id: uuid.UUID
    report_type: str  # wrong_answer, unclear, off_topic, duplicate, grammar, other
    comment: str | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    reported_by: uuid.UUID
    report_type: str
    comment: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportResolveRequest(BaseModel):
    status: str  # fixed, rejected