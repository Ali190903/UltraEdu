import json

from core.gemini_client import GeminiClient
from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper, DIM_TESTS_COLLECTION
from generation.prompts import VALIDATION_PROMPT
from data_pipeline.json_utils import parse_llm_json


class ValidationStage:
    """Stage 3: Validate generated question via similarity check + LLM review."""

    def __init__(
        self,
        gemini: GeminiClient,
        embedding: EmbeddingClient,
        qdrant: QdrantWrapper,
        similarity_threshold: float = 0.85,
    ):
        self.gemini = gemini
        self.embedding = embedding
        self.qdrant = qdrant
        self.similarity_threshold = similarity_threshold

    async def validate(
        self,
        question: dict,
        textbook_context: list[dict],
        bloom_level: str,
    ) -> dict:
        # Stage 3A: Semantic similarity check against existing DIM questions
        question_vector = await self.embedding.embed(question["question_text"])
        similar = self.qdrant.search(
            collection=DIM_TESTS_COLLECTION,
            vector=question_vector,
            limit=3,
        )

        max_similarity = max((s["score"] for s in similar), default=0.0)

        if max_similarity > self.similarity_threshold:
            return {
                "answer_correct": False,
                "textbook_aligned": False,
                "original": False,
                "bloom_accurate": False,
                "grammar_quality": False,
                "passed": False,
                "feedback": f"Too similar to existing DIM question (similarity: {max_similarity:.2f})",
                "similarity_score": max_similarity,
            }

        # Stage 3B: LLM self-validation with 5 criteria
        context_text = "\n".join(
            c["payload"].get("text_content", "") for c in textbook_context
        )

        prompt = VALIDATION_PROMPT.format(
            question_json=json.dumps(question, ensure_ascii=False),
            textbook_context=context_text,
            bloom_level=bloom_level,
        )

        response = await self.gemini.generate_json(prompt)
        result = parse_llm_json(response)
        if isinstance(result, list):
            result = result[0]
        result["similarity_score"] = max_similarity
        return result