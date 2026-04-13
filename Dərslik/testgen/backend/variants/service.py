import asyncio
import logging
import random
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.variant import Variant, VariantQuestion
from models.question import Question
from generation.pipeline import GenerationPipeline
from core.qdrant_client import QdrantWrapper, DIM_TESTS_COLLECTION
from data_pipeline.dim_blocks import DIM_MATH_BLOCKS

logger = logging.getLogger("testgen.variants")

REFILL_ROUNDS = 1  # how many extra generation rounds to fill failed slots


def _dim_math_block_dist(raw_counts: dict[str, int], total_questions: int) -> dict[str, int]:
    dist: dict[str, int] = {}
    
    # Calculate available topics in each block and their frequencies
    block_availability = {}
    for block_name, block_info in DIM_MATH_BLOCKS.items():
        avail = {t: raw_counts[t] for t in block_info["topics"] if t in raw_counts}
        block_availability[block_name] = avail

    # Distribute target counts, absorbing shortfalls from empty blocks (e.g., Funksiyalar)
    final_block_targets = {}
    shortfall = 0
    for block_name, block_info in DIM_MATH_BLOCKS.items():
        if not block_availability[block_name]:
            shortfall += block_info["target_count"]
            final_block_targets[block_name] = 0
        else:
            final_block_targets[block_name] = block_info["target_count"]
    
    # Distribute shortfall iteratively to blocks that have available topics
    active_blocks = [b for b, a in block_availability.items() if a]
    while shortfall > 0 and active_blocks:
        active_blocks.sort(key=lambda b: sum(block_availability[b].values()), reverse=True)
        final_block_targets[active_blocks[0]] += 1
        shortfall -= 1
        # Round-robin
        active_blocks = active_blocks[1:] + [active_blocks[0]]

    # For each block, pick topics proportional to their frequency, hard cap at 2 per topic
    for block_name, target in final_block_targets.items():
        if target == 0:
            continue
        avail = block_availability[block_name]
        sorted_avail = sorted(avail.items(), key=lambda x: x[1], reverse=True)
        
        while target > 0 and sorted_avail:
            made_progress = False
            for i in range(len(sorted_avail)):
                if target == 0: break
                t, _ = sorted_avail[i]
                if dist.get(t, 0) < 2:
                    dist[t] = dist.get(t, 0) + 1
                    target -= 1
                    made_progress = True
            
            if not made_progress:
                shortfall += target
                target = 0
                break

    # If any shortfall remains after anti-clustering cap, dump it back into top overall topics
    if shortfall > 0:
        sorted_all = sorted(raw_counts.items(), key=lambda x: x[1], reverse=True)
        for t, _ in sorted_all:
            if shortfall == 0: break
            # Soften cap to 3 for spillovers just to properly satisfy 25 questions
            if dist.get(t, 0) < 3:
                dist[t] = dist.get(t, 0) + 1
                shortfall -= 1

    # Exact adjustment in case of any remaining drift
    diff = total_questions - sum(dist.values())
    if diff != 0 and dist:
        largest = max(dist, key=dist.get)
        dist[largest] += diff
        
    return dist


def _auto_topic_dist(qdrant: QdrantWrapper, subject: str, total_questions: int) -> dict[str, int]:
    """Distribute questions across DIM topics for maximum variety using official block rules."""
    raw_counts = qdrant.get_topic_distribution(DIM_TESTS_COLLECTION, subject)
    if not raw_counts:
        return {subject: total_questions}

    if subject == "riyaziyyat":
        return _dim_math_block_dist(raw_counts, total_questions)

    # Fallback for other subjects
    sorted_topics = sorted(raw_counts.items(), key=lambda x: x[1], reverse=True)
    chosen = sorted_topics[: min(len(sorted_topics), total_questions)]

    dist: dict[str, int] = {t: 1 for t, _ in chosen}
    remaining = total_questions - len(chosen)

    if remaining > 0:
        chosen_total = sum(c for _, c in chosen)
        for topic, count in chosen:
            extra = round(count / chosen_total * remaining)
            dist[topic] += extra

    diff = total_questions - sum(dist.values())
    if diff != 0:
        largest = max(dist, key=dist.get)
        dist[largest] = max(1, dist[largest] + diff)

    return dist


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

    # Build task list — expand topic_dist and difficulty_dist into matching-length
    # lists, shuffle both, and zip so each slot gets a proportional topic paired
    # with a proportional difficulty. Avoids A→B→C→A→B→C cyclic repetition.
    topics_expanded: list[str] = []
    for t, cnt in topic_dist.items():
        topics_expanded.extend([t] * cnt)
    difficulties_expanded: list[str] = []
    for d, cnt in difficulty_dist.items():
        difficulties_expanded.extend([d] * cnt)

    # If counts don't match, truncate/pad to difficulty_dist total (authoritative)
    target_total = sum(difficulty_dist.values())
    if len(topics_expanded) < target_total:
        topic_pool = list(topic_dist.keys()) or [subject]
        while len(topics_expanded) < target_total:
            topics_expanded.append(topic_pool[len(topics_expanded) % len(topic_pool)])
    topics_expanded = topics_expanded[:target_total]
    difficulties_expanded = difficulties_expanded[:target_total]

    random.shuffle(topics_expanded)
    random.shuffle(difficulties_expanded)
    tasks: list[tuple[str, str]] = list(zip(topics_expanded, difficulties_expanded))

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

    async def run_batch(batch_tasks: list[tuple[str, str]]):
        return await asyncio.gather(
            *[gen_one(t, d) for t, d in batch_tasks],
            return_exceptions=True,
        )

    # Round 1: full batch
    results = await run_batch(tasks)
    successful: list[tuple[tuple[str, str], dict]] = [
        (tasks[i], r)
        for i, r in enumerate(results)
        if not isinstance(r, Exception) and r["validation"]["passed"]
    ]

    # Refill rounds for failed slots — keep firing until we hit target or exhaust rounds
    refill_round = 0
    while len(successful) < target_total and refill_round < REFILL_ROUNDS:
        refill_round += 1
        needed = target_total - len(successful)
        topic_pool = list(topic_dist.keys()) or [subject]
        refill_tasks: list[tuple[str, str]] = []
        for _ in range(needed):
            refill_tasks.append(
                (random.choice(topic_pool), random.choice(difficulties_expanded))
            )
        logger.info(
            "[variant] refill round %d: generating %d replacement questions",
            refill_round, needed,
        )
        refill_results = await run_batch(refill_tasks)
        for i, r in enumerate(refill_results):
            if not isinstance(r, Exception) and r["validation"]["passed"]:
                successful.append((refill_tasks[i], r))
            if len(successful) >= target_total:
                break

    exc_count = sum(1 for r in results if isinstance(r, Exception))
    failed_val_count = sum(
        1 for r in results
        if not isinstance(r, Exception) and not r["validation"]["passed"]
    )
    logger.info(
        "[variant] title=%r target=%d final_passed=%d round1_failed_validation=%d round1_exceptions=%d refill_rounds=%d",
        title, target_total, len(successful), failed_val_count, exc_count, refill_round,
    )

    for order, ((topic, difficulty), result) in enumerate(successful, start=1):
        q = result["question"]
        question = Question(
            subject=subject,
            grade=grade,
            topic=topic,
            question_type="mcq",
            difficulty=difficulty,
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

        vq = VariantQuestion(variant_id=variant.id, question_id=question.id, order_number=order)
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