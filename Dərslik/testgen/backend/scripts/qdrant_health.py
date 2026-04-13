"""Quick Qdrant health check.

Usage (inside backend container):
    python scripts/qdrant_health.py
    python scripts/qdrant_health.py --subject math --grade 11

Reports point counts and subject/topic distribution so we can verify the RAG
corpus is actually populated before blaming the retrieval stage.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings  # noqa: E402
from core.qdrant_client import (  # noqa: E402
    QdrantWrapper,
    TEXTBOOKS_COLLECTION,
    DIM_TESTS_COLLECTION,
)


def scroll_all(wrapper: QdrantWrapper, collection: str) -> list[dict]:
    points: list[dict] = []
    offset = None
    while True:
        batch, next_offset = wrapper.client.scroll(
            collection_name=collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for p in batch:
            points.append(p.payload or {})
        if next_offset is None:
            break
        offset = next_offset
    return points


def describe(wrapper: QdrantWrapper, collection: str, subject_filter: str | None, grade_filter: int | None):
    print(f"\n=== {collection} ===")
    try:
        total = wrapper.count(collection)
    except Exception as e:
        print(f"  ERROR: collection missing or unreachable: {e!r}")
        return

    print(f"  total points: {total}")
    if total == 0:
        print("  !! EMPTY — ingestion has not run for this collection")
        return

    payloads = scroll_all(wrapper, collection)
    subjects = Counter(p.get("subject", "<none>") for p in payloads)
    grades = Counter(p.get("grade", "<none>") for p in payloads)

    print(f"  subjects: {dict(subjects)}")
    print(f"  grades:   {dict(grades)}")

    if subject_filter:
        scoped = [p for p in payloads if p.get("subject") == subject_filter]
        if grade_filter is not None:
            scoped = [p for p in scoped if p.get("grade") == grade_filter]
        topics = Counter(p.get("topic", "<none>") for p in scoped)
        print(f"  topics for subject={subject_filter} grade={grade_filter}: {len(scoped)} points")
        for topic, count in topics.most_common(20):
            print(f"    {count:4d}  {topic}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default=None)
    parser.add_argument("--grade", type=int, default=None)
    args = parser.parse_args()

    print(f"qdrant url: {settings.qdrant_url}")
    wrapper = QdrantWrapper(url=settings.qdrant_url)

    describe(wrapper, TEXTBOOKS_COLLECTION, args.subject, args.grade)
    describe(wrapper, DIM_TESTS_COLLECTION, args.subject, args.grade)


if __name__ == "__main__":
    main()
