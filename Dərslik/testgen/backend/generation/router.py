from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.database import get_db
from core.gemini_client import GeminiClient
from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper
from auth.security import get_current_user
from models.user import User
from models.question import Question
from models.generation_log import GenerationLog
from generation.schemas import GenerateRequest
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.pipeline import GenerationPipeline

router = APIRouter(prefix="/api/generation", tags=["generation"])


def get_pipeline() -> GenerationPipeline:
    gemini = GeminiClient(api_key=settings.gemini_api_key)
    embedding = EmbeddingClient(api_key=settings.gemini_api_key)
    qdrant = QdrantWrapper(url=settings.qdrant_url)
    return GenerationPipeline(
        retrieval=RetrievalStage(embedding=embedding, qdrant=qdrant),
        generator=GenerationStage(gemini=gemini),
        validator=ValidationStage(
            gemini=gemini,
            embedding=embedding,
            qdrant=qdrant,
            similarity_threshold=settings.similarity_threshold,
        ),
        max_attempts=settings.max_generation_attempts,
    )


@router.post("/generate")
async def generate_question(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    pipeline: GenerationPipeline = Depends(get_pipeline),
):
    result = await pipeline.run(
        subject=req.subject,
        grade=req.grade,
        topic=req.topic,
        difficulty=req.difficulty,
        question_type=req.question_type,
    )

    # Save question to DB regardless of validation result (return with warning if failed)
    q = result["question"]
    question = Question(
        subject=req.subject,
        grade=req.grade,
        topic=req.topic,
        question_type=req.question_type,
        difficulty=req.difficulty,
        bloom_level=q["bloom_level"],
        question_text=q["question_text"],
        options=q.get("options"),
        matching_pairs=q.get("matching_pairs"),
        correct_answer=q["correct_answer"],
        explanation=q["explanation"],
        latex_content=q.get("latex_content"),
        source_reference=q["source_reference"],
        similarity_score=result["validation"].get("similarity_score", 0.0),
        validation_result=result["validation"],
        created_by=user.id,
    )
    db.add(question)
    await db.flush()

    validation_passed = result["validation"].get("passed", False)
    log = GenerationLog(
        user_id=user.id,
        question_id=question.id,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        retrieval_time=result["timing"]["retrieval"],
        generation_time=result["timing"]["generation"],
        validation_time=result["timing"]["validation"],
        total_time=result["timing"]["total"],
        attempts=result["attempts"],
        success=validation_passed,
    )
    db.add(log)
    await db.commit()

    return {
        "question": q,
        "question_id": str(question.id),
        "attempts": result["attempts"],
        "timing": result["timing"],
        "validation": result["validation"],
        "validation_passed": validation_passed,
    }