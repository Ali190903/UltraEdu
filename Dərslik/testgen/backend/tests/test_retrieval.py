"""Tests for retrieval stage — dual Qdrant search (Task 12)."""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_retrieval_returns_textbook_and_dim_context():
    """Stage 1: embed query → search textbooks + dim_tests → return both."""
    from generation.retrieval import RetrievalStage

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.side_effect = [
        [{"payload": {"text_content": "Tənliklər mövzusu...", "pages": "20-22"}, "score": 0.9}],
        [{"payload": {"question_text": "x+3=5 olduqda x=?", "options": "A:2 B:3", "correct_answer": "A"}, "score": 0.88}],
    ]

    stage = RetrievalStage(embedding=mock_embedding, qdrant=mock_qdrant)
    result = await stage.retrieve(
        subject="riyaziyyat",
        grade=9,
        topic="Tənliklər",
    )

    assert "textbook_context" in result
    assert "dim_examples" in result
    assert len(result["textbook_context"]) == 1
    assert len(result["dim_examples"]) == 1
    mock_embedding.embed.assert_awaited_once()
    assert mock_qdrant.search.call_count == 2


@pytest.mark.asyncio
async def test_retrieval_passes_correct_filters():
    """Verify filters match spec §7.1: textbooks filter by subject+grade, dim_tests by subject."""
    from generation.retrieval import RetrievalStage

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.5] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = []

    stage = RetrievalStage(embedding=mock_embedding, qdrant=mock_qdrant)
    await stage.retrieve(subject="ingilis_dili", grade=11, topic="Tenses")

    # First call: textbooks — filter by subject AND grade
    tb_call = mock_qdrant.search.call_args_list[0]
    assert tb_call.kwargs["filters"] == {"subject": "ingilis_dili", "grade": 11}

    # Second call: dim_tests — filter by subject only
    dim_call = mock_qdrant.search.call_args_list[1]
    assert dim_call.kwargs["filters"] == {"subject": "ingilis_dili"}


@pytest.mark.asyncio
async def test_retrieval_uses_correct_collections():
    """Verify correct Qdrant collection names are used."""
    from generation.retrieval import RetrievalStage
    from core.qdrant_client import TEXTBOOKS_COLLECTION, DIM_TESTS_COLLECTION

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.0] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = []

    stage = RetrievalStage(embedding=mock_embedding, qdrant=mock_qdrant)
    await stage.retrieve(subject="riyaziyyat", grade=9, topic="Həndəsə")

    tb_call = mock_qdrant.search.call_args_list[0]
    assert tb_call.kwargs["collection"] == TEXTBOOKS_COLLECTION

    dim_call = mock_qdrant.search.call_args_list[1]
    assert dim_call.kwargs["collection"] == DIM_TESTS_COLLECTION


@pytest.mark.asyncio
async def test_retrieval_custom_limits():
    """Verify custom limit parameters are passed through."""
    from generation.retrieval import RetrievalStage

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.0] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = []

    stage = RetrievalStage(embedding=mock_embedding, qdrant=mock_qdrant)
    await stage.retrieve(
        subject="az_dili", grade=9, topic="Fonetika",
        textbook_limit=3, dim_limit=10,
    )

    tb_call = mock_qdrant.search.call_args_list[0]
    assert tb_call.kwargs["limit"] == 3

    dim_call = mock_qdrant.search.call_args_list[1]
    assert dim_call.kwargs["limit"] == 10


@pytest.mark.asyncio
async def test_retrieval_embeds_topic_in_query():
    """Query text should include subject and topic for relevant search."""
    from generation.retrieval import RetrievalStage

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.0] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = []

    stage = RetrievalStage(embedding=mock_embedding, qdrant=mock_qdrant)
    await stage.retrieve(subject="riyaziyyat", grade=11, topic="Triqonometriya")

    # Check that embed was called with text containing subject and topic
    embed_arg = mock_embedding.embed.call_args[0][0]
    assert "riyaziyyat" in embed_arg.lower()
    assert "triqonometriya" in embed_arg.lower()