import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from models.user import User
from reports.schemas import ReportCreateRequest, ReportResponse, ReportResolveRequest
from reports.service import create_report, list_reports, resolve_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
async def report_question(
    req: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = await create_report(db, req.question_id, user.id, req.report_type, req.comment)
    return ReportResponse.model_validate(report)


@router.get("", response_model=list[ReportResponse])
async def list_all(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    reports = await list_reports(db, status)
    return [ReportResponse.model_validate(r) for r in reports]


@router.patch("/{report_id}", response_model=ReportResponse)
async def resolve(
    report_id: uuid.UUID,
    req: ReportResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    report = await resolve_report(db, report_id, req.status)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)