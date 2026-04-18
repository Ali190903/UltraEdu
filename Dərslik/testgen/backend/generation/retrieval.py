from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper, TEXTBOOKS_COLLECTION, DIM_TESTS_COLLECTION


class RetrievalStage:
    """Stage 1: Retrieve textbook context and DIM examples via Qdrant."""

    def __init__(self, embedding: EmbeddingClient, qdrant: QdrantWrapper):
        self.embedding = embedding
        self.qdrant = qdrant

    async def retrieve(
        self,
        subject: str,
        grade: int,
        topic: str,
        textbook_limit: int = 5,
        dim_limit: int = 5,
    ) -> dict:
        query_text = f"{subject} {topic} grade {grade}"
        query_vector = await self.embedding.embed(query_text)

        textbook_context = self.qdrant.search(
            collection=TEXTBOOKS_COLLECTION,
            vector=query_vector,
            filters={"subject": subject, "grade": grade},
            limit=textbook_limit,
        )

        # Buraxılış riyaziyyat: calculus and format-label topics indexed from older
        # DIM data must not appear as examples — they would contaminate LLM output.
        dim_exclude = None
        if subject == "riyaziyyat":
            dim_exclude = {
                "topic": [
                    "İbtidai funksiya və inteqral",
                    "Törəmə və tətbiqləri",
                    "Situasiya",
                    "Situasiya məsələləri",
                ]
            }

        dim_examples = self.qdrant.search(
            collection=DIM_TESTS_COLLECTION,
            vector=query_vector,
            filters={"subject": subject, "needs_review": False},
            exclude_values=dim_exclude,
            limit=dim_limit,
        )

        return {
            "textbook_context": textbook_context,
            "dim_examples": dim_examples,
        }