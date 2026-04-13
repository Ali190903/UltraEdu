import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)

from core.database import get_db
from auth.security import get_current_user
from models.user import User
from models.question import Question
from models.generation_log import GenerationLog

app = FastAPI(title="TestGen AI", version="0.1.0")

import os as _os

_cors_origins = _os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


from auth.router import router as auth_router
from generation.router import router as generation_router
from questions.router import router as questions_router
from subjects.router import router as subjects_router
from variants.router import router as variants_router
from reports.router import router as reports_router

app.include_router(auth_router)
app.include_router(generation_router)
app.include_router(questions_router)
app.include_router(subjects_router)
app.include_router(variants_router)
app.include_router(reports_router)


@app.get("/api/stats/dashboard")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_questions = (await db.execute(select(func.count(Question.id)))).scalar() or 0
    total_generations = (await db.execute(select(func.count(GenerationLog.id)))).scalar() or 0
    success_count = (await db.execute(
        select(func.count(GenerationLog.id)).where(GenerationLog.success == True)
    )).scalar() or 0
    avg_time = (await db.execute(select(func.avg(GenerationLog.total_time)))).scalar() or 0

    return {
        "total_questions": total_questions,
        "total_generations": total_generations,
        "success_rate": (success_count / total_generations * 100) if total_generations > 0 else 0,
        "avg_generation_time": round(avg_time, 2),
    }