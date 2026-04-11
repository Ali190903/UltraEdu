from pydantic import BaseModel


class SubjectInfo(BaseModel):
    id: str
    name: str
    name_az: str


class TopicInfo(BaseModel):
    chapter: str
    chapter_order: int
    topic: str
    subtopic: str | None
    page_start: int | None
    page_end: int | None

    model_config = {"from_attributes": True}