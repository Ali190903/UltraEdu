import time
from qdrant_client import QdrantClient, models

TEXTBOOKS_COLLECTION = "textbooks"
DIM_TESTS_COLLECTION = "dim_tests"
VECTOR_DIM = 3072


class QdrantWrapper:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)
        self._topic_dist_cache = {}  # In-memory TTL cache

    def ensure_collections(self):
        for name in [TEXTBOOKS_COLLECTION, DIM_TESTS_COLLECTION]:
            collections = [c.name for c in self.client.get_collections().collections]
            if name not in collections:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(size=VECTOR_DIM, distance=models.Distance.COSINE),
                )

    def search(
        self,
        collection: str,
        vector: list[float],
        filters: dict | None = None,
        exclude_values: dict | None = None,
        limit: int = 5,
    ) -> list[dict]:
        query_filter = None
        must_conditions = []
        must_not_conditions = []
        if filters:
            for key, value in filters.items():
                must_conditions.append(
                    models.FieldCondition(key=key, match=models.MatchValue(value=value))
                )
        if exclude_values:
            for key, values in exclude_values.items():
                for value in values:
                    must_not_conditions.append(
                        models.FieldCondition(key=key, match=models.MatchValue(value=value))
                    )
        if must_conditions or must_not_conditions:
            query_filter = models.Filter(
                must=must_conditions or None,
                must_not=must_not_conditions or None,
            )

        results = self.client.query_points(
            collection_name=collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
        )
        return [
            {"payload": hit.payload, "score": hit.score}
            for hit in results.points
        ]

    def upsert(self, collection: str, points: list[dict]):
        qdrant_points = [
            models.PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        self.client.upsert(collection_name=collection, points=qdrant_points)

    def count(self, collection: str) -> int:
        return self.client.count(collection_name=collection).count

    def get_topic_distribution(self, collection: str, subject: str) -> dict[str, int]:
        """Scroll all points in a collection for a subject and count topic occurrences."""
        cache_key = f"{collection}_{subject}"
        cached = self._topic_dist_cache.get(cache_key)
        # Əgər cache varsa və 1 saatı (3600 san) keçməyibsə, cache-i qaytar
        if cached and (time.time() - cached["time"] < 3600):
            return cached["data"]

        topic_counts: dict[str, int] = {}
        offset = None
        while True:
            results, next_offset = self.client.scroll(
                collection_name=collection,
                scroll_filter=models.Filter(
                    must=[models.FieldCondition(key="subject", match=models.MatchValue(value=subject))]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for point in results:
                topic = point.payload.get("topic", subject)
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            if next_offset is None:
                break
            offset = next_offset

        self._topic_dist_cache[cache_key] = {"time": time.time(), "data": topic_counts}
        return topic_counts