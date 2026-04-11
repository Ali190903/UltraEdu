import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from models.user import User
from questions.schemas import QuestionResponse, QuestionUpdate, QuestionListResponse
from questions.service import list_questions, get_question, update_question, delete_question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=QuestionListResponse)
async def list_all(
    subject: str | None = None,
    grade: int | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    status: str = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = await list_questions(db, subject, grade, topic, difficulty, status, page, page_size)
    return QuestionListResponse(
        items=[QuestionResponse.model_validate(q) for q in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_one(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    question = await get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionResponse.model_validate(question)


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update(
    question_id: uuid.UUID,
    body: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    question = await update_question(db, question_id, body.model_dump(exclude_unset=True))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionResponse.model_validate(question)


@router.delete("/{question_id}", status_code=204)
async def delete(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    if not await delete_question(db, question_id):
        raise HTTPException(status_code=404, detail="Question not found")