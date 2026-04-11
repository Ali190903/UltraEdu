import uuid

from sqlalchemy import select, func, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from models.question import Question
from models.generation_log import GenerationLog


async def list_questions(
    db: AsyncSession,
    subject: str | None = None,
    grade: int | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    status: str = "active",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Question], int]:
    query = select(Question)
    count_query = select(func.count(Question.id))

    if subject:
        query = query.where(Question.subject == subject)
        count_query = count_query.where(Question.subject == subject)
    if grade:
        query = query.where(Question.grade == grade)
        count_query = count_query.where(Question.grade == grade)
    if topic:
        query = query.where(Question.topic == topic)
        count_query = count_query.where(Question.topic == topic)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
        count_query = count_query.where(Question.difficulty == difficulty)
    if status:
        query = query.where(Question.status == status)
        count_query = count_query.where(Question.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Question.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_question(db: AsyncSession, question_id: uuid.UUID) -> Question | None:
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def update_question(db: AsyncSession, question_id: uuid.UUID, updates: dict) -> Question | None:
    question = await get_question(db, question_id)
    if not question:
        return None
    for key, value in updates.items():
        if value is not None:
            setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: uuid.UUID) -> bool:
    question = await get_question(db, question_id)
    if not question:
        return False
    # Nullify FK references in generation_logs before deleting
    await db.execute(
        sa_update(GenerationLog)
        .where(GenerationLog.question_id == question_id)
        .values(question_id=None)
    )
    await db.delete(question)
    await db.commit()
    return True