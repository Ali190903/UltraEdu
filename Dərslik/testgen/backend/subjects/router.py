from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.topic import Topic
from subjects.schemas import SubjectInfo, TopicInfo

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

SUBJECTS = [
    SubjectInfo(id="az_dili", name="Azerbaijani Language", name_az="Azərbaycan dili"),
    SubjectInfo(id="riyaziyyat", name="Mathematics", name_az="Riyaziyyat"),
    SubjectInfo(id="ingilis", name="English Language", name_az="İngilis dili"),
]


@router.get("", response_model=list[SubjectInfo])
async def list_subjects():
    return SUBJECTS


@router.get("/{subject_id}/topics", response_model=list[TopicInfo])
async def get_topics(
    subject_id: str,
    grade: int = Query(..., ge=9, le=11),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Topic)
        .where(Topic.subject == subject_id, Topic.grade == grade)
        .order_by(Topic.chapter_order, Topic.topic)
    )
    topics = result.scalars().all()
    return [TopicInfo.model_validate(t) for t in topics]