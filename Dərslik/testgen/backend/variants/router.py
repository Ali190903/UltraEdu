import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.database import get_db
from core.gemini_client import GeminiClient
from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper
from auth.security import get_current_user
from models.user import User
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.pipeline import GenerationPipeline
from variants.schemas import VariantCreateRequest, VariantResponse
from variants.service import create_variant, list_variants, get_variant_with_questions
from variants.export import export_json, export_pdf, export_word, export_text

router = APIRouter(prefix="/api/variants", tags=["variants"])


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


@router.post("/generate", response_model=VariantResponse, status_code=201)
async def generate_variant(
    req: VariantCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")

    pipeline = get_pipeline()
    qdrant = QdrantWrapper(url=settings.qdrant_url)
    variant = await create_variant(
        db=db,
        pipeline=pipeline,
        qdrant=qdrant,
        user_id=user.id,
        title=req.title,
        subject=req.subject,
        grade=req.grade,
        total_questions=req.total_questions,
        difficulty_dist=req.difficulty_dist,
        topic_dist=req.topic_dist,
    )
    return VariantResponse.model_validate(variant)


@router.get("", response_model=list[VariantResponse])
async def list_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    variants = await list_variants(db, user.id)
    return [VariantResponse.model_validate(v) for v in variants]


@router.get("/{variant_id}")
async def get_one(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await get_variant_with_questions(db, variant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Variant not found")

    variant = data["variant"]
    return {
        "variant": {
            "id": str(variant.id),
            "title": variant.title,
            "subject": variant.subject,
            "total_questions": variant.total_questions,
            "difficulty_dist": variant.difficulty_dist,
            "created_at": variant.created_at.isoformat(),
        },
        "questions": [
            {
                "order": item["order"],
                "question": {
                    "id": str(item["question"].id),
                    "question_text": item["question"].question_text,
                    "options": item["question"].options,
                    "correct_answer": item["question"].correct_answer,
                    "explanation": item["question"].explanation,
                    "latex_content": item["question"].latex_content,
                    "source_reference": item["question"].source_reference,
                    "bloom_level": item["question"].bloom_level,
                    "difficulty": item["question"].difficulty,
                    "topic": item["question"].topic,
                },
            }
            for item in data["questions"]
        ],
    }


@router.get("/{variant_id}/export")
async def export(
    variant_id: uuid.UUID,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await get_variant_with_questions(db, variant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Variant not found")

    if format == "json":
        content = export_json(data)
        return Response(content=content, media_type="application/json",
                        headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.json"})
    elif format == "pdf":
        content = await export_pdf(data)
        return Response(content=content, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.pdf"})
    elif format == "word":
        content = await export_word(data)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.docx"},
        )
    elif format == "text":
        content = export_text(data).encode("utf-8")
        return Response(
            content=content,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.txt"},
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use: json, pdf, word, text")