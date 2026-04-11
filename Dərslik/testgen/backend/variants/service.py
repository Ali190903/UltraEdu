import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.variant import Variant, VariantQuestion
from models.question import Question
from generation.pipeline import GenerationPipeline
from core.qdrant_client import QdrantWrapper, DIM_TESTS_COLLECTION


def _auto_topic_dist(qdrant: QdrantWrapper, subject: str, total_questions: int) -> dict[str, int]:
    """Distribute questions proportionally to DIM topic frequency."""
    raw_counts = qdrant.get_topic_distribution(DIM_TESTS_COLLECTION, subject)
    if not raw_counts:
        return {subject: total_questions}

    total_dim = sum(raw_counts.values())
    dist: dict[str, int] = {}
    assigned = 0
    sorted_topics = sorted(raw_counts.items(), key=lambda x: x[1], reverse=True)
    for topic, count in sorted_topics:
        n = round(count / total_dim * total_questions)
        if n > 0:
            dist[topic] = n
            assigned += n

    # Adjust rounding: add/remove from largest topic
    diff = total_questions - assigned
    if diff != 0 and dist:
        largest = next(iter(dist))
        dist[largest] = max(1, dist[largest] + diff)

    return dist if dist else {subject: total_questions}


async def create_variant(
    db: AsyncSession,
    pipeline: GenerationPipeline,
    qdrant: QdrantWrapper,
    user_id: uuid.UUID,
    title: str,
    subject: str,
    grade: int,
    total_questions: int,
    difficulty_dist: dict,
    topic_dist: dict | None = None,
) -> Variant:
    variant = Variant(
        title=title,
        subject=subject,
        total_questions=total_questions,
        difficulty_dist=difficulty_dist,
        created_by=user_id,
    )
    db.add(variant)
    await db.flush()

    # Auto mode: distribute topics proportionally to DIM exam frequency
    if not topic_dist:
        topic_dist = _auto_topic_dist(qdrant, subject, total_questions)

    # Build task list from difficulty + topic distributions
    tasks = []
    topic_list = list(topic_dist.keys())
    for difficulty, count in difficulty_dist.items():
        for i in range(count):
            topic = topic_list[i % len(topic_list)]
            tasks.append((topic, difficulty))

    # Generate questions (5 concurrent)
    semaphore = asyncio.Semaphore(5)

    async def gen_one(topic: str, difficulty: str):
        async with semaphore:
            return await pipeline.run(
                subject=subject,
                grade=grade,
                topic=topic,
                difficulty=difficulty,
            )

    results = await asyncio.gather(
        *[gen_one(t, d) for t, d in tasks],
        return_exceptions=True,
    )

    for i, result in enumerate(results):
        if isinstance(result, Exception) or not result["validation"]["passed"]:
            continue

        q = result["question"]
        question = Question(
            subject=subject,
            grade=grade,
            topic=tasks[i][0],
            question_type="mcq",
            difficulty=tasks[i][1],
            bloom_level=q["bloom_level"],
            question_text=q["question_text"],
            options=q.get("options"),
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            latex_content=q.get("latex_content"),
            source_reference=q["source_reference"],
            similarity_score=result["validation"].get("similarity_score", 0.0),
            validation_result=result["validation"],
            created_by=user_id,
        )
        db.add(question)
        await db.flush()

        vq = VariantQuestion(variant_id=variant.id, question_id=question.id, order_number=i + 1)
        db.add(vq)

    await db.commit()
    await db.refresh(variant)
    return variant


async def list_variants(db: AsyncSession, user_id: uuid.UUID) -> list[Variant]:
    result = await db.execute(
        select(Variant).where(Variant.created_by == user_id).order_by(Variant.created_at.desc())
    )
    return result.scalars().all()


async def get_variant_with_questions(db: AsyncSession, variant_id: uuid.UUID) -> dict | None:
    result = await db.execute(select(Variant).where(Variant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        return None

    vq_result = await db.execute(
        select(VariantQuestion, Question)
        .join(Question, VariantQuestion.question_id == Question.id)
        .where(VariantQuestion.variant_id == variant_id)
        .order_by(VariantQuestion.order_number)
    )
    questions = [{"order": vq.order_number, "question": q} for vq, q in vq_result.all()]

    return {"variant": variant, "questions": questions}