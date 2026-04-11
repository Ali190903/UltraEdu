import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.report import Report
from models.question import Question


async def create_report(
    db: AsyncSession,
    question_id: uuid.UUID,
    user_id: uuid.UUID,
    report_type: str,
    comment: str | None,
) -> Report:
    report = Report(
        question_id=question_id,
        reported_by=user_id,
        report_type=report_type,
        comment=comment,
    )
    db.add(report)

    # Increment report count on question
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question:
        question.report_count += 1
        if question.report_count >= 3:
            question.status = "reported"

    await db.commit()
    await db.refresh(report)
    return report


async def list_reports(db: AsyncSession, status: str | None = None) -> list[Report]:
    query = select(Report).order_by(Report.created_at.desc())
    if status:
        query = query.where(Report.status == status)
    result = await db.execute(query)
    return result.scalars().all()


async def resolve_report(db: AsyncSession, report_id: uuid.UUID, new_status: str) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        return None
    report.status = new_status
    await db.commit()
    await db.refresh(report)
    return report