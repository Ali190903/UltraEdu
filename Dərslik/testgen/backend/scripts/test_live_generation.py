"""Live end-to-end: trigger 3 generations with varied topics/difficulty and
check that structural validator + sanitizer produce clean output.

Run inside backend container:
    docker exec -w /app testgen-backend-1 python -m scripts.test_live_generation
"""
import asyncio
import os

from core.gemini_client import GeminiClient
from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper
from generation.pipeline import GenerationPipeline, _structural_check
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage


async def main():
    gemini = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
    embedding = EmbeddingClient(api_key=os.environ["GEMINI_API_KEY"])
    qdrant = QdrantWrapper(url=os.environ["QDRANT_URL"])
    pipeline = GenerationPipeline(
        retrieval=RetrievalStage(embedding, qdrant),
        generator=GenerationStage(gemini),
        validator=ValidationStage(gemini, embedding, qdrant),
        max_attempts=3,
    )

    # 3 topics that previously produced defects
    tasks = [
        ("Rasional kəsrlər", "medium"),
        ("Ədədi ardıcıllıqlar. Silsilələr", "easy"),
        ("Həndəsənin əsas anlayışları", "hard"),
    ]

    for topic, diff in tasks:
        print(f"\n=== {topic} / {diff} ===")
        result = await pipeline.run(
            subject="riyaziyyat",
            grade=11,
            topic=topic,
            difficulty=diff,
        )
        q = result["question"]
        print("passed:", result["validation"].get("passed"))
        print("attempts:", result["attempts"])
        struct_ok, reason = _structural_check(q, "riyaziyyat", 11)
        print("structural_ok:", struct_ok, reason)
        print("question_text:", q.get("question_text", "")[:120])
        opts = q.get("options") or {}
        print("options keys:", sorted(opts.keys()))
        for k, v in opts.items():
            print(f"  {k}: {v[:80]}")
        print("correct_answer:", q.get("correct_answer"))


if __name__ == "__main__":
    asyncio.run(main())