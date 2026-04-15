"""Singleton API clients — created once and reused across requests."""

from functools import lru_cache

from config import settings
from core.gemini_client import GeminiClient
from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.pipeline import GenerationPipeline


@lru_cache(maxsize=1)
def get_gemini_client() -> GeminiClient:
    return GeminiClient(api_key=settings.gemini_api_key)


@lru_cache(maxsize=1)
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient(api_key=settings.gemini_api_key)


@lru_cache(maxsize=1)
def get_qdrant() -> QdrantWrapper:
    return QdrantWrapper(url=settings.qdrant_url)


def get_pipeline() -> GenerationPipeline:
    """Build pipeline from cached singletons."""
    gemini = get_gemini_client()
    embedding = get_embedding_client()
    qdrant = get_qdrant()
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
