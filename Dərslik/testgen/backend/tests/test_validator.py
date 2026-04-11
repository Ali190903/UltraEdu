"""Tests for validation stage (Task 13 — Stage 3)."""

import json

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_validator_passes_good_question():
    """Stage 3: similarity OK + LLM validation passes → passed=True."""
    from generation.validator import ValidationStage

    validation = {
        "answer_correct": True,
        "textbook_aligned": True,
        "original": True,
        "bloom_accurate": True,
        "grammar_quality": True,
        "passed": True,
        "feedback": "Good question",
    }

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value=json.dumps(validation))

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.6}]

    stage = ValidationStage(
        gemini=mock_gemini, embedding=mock_embedding,
        qdrant=mock_qdrant, similarity_threshold=0.85,
    )

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question,
        textbook_context=[{"payload": {"text_content": "Content"}}],
        bloom_level="Remember and Understand",
    )

    assert result["passed"] is True
    assert result["similarity_score"] == 0.6


@pytest.mark.asyncio
async def test_validator_rejects_too_similar():
    """Stage 3A: similarity > threshold → reject immediately without LLM call."""
    from generation.validator import ValidationStage

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock()  # should NOT be called

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.92}]

    stage = ValidationStage(
        gemini=mock_gemini, embedding=mock_embedding,
        qdrant=mock_qdrant, similarity_threshold=0.85,
    )

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question, textbook_context=[], bloom_level="Remember and Understand",
    )

    assert result["passed"] is False
    assert result["original"] is False
    assert "similar" in result["feedback"].lower()
    # LLM validation should be skipped when similarity is too high
    mock_gemini.generate_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_validator_llm_rejects_bad_answer():
    """Stage 3B: LLM says answer_correct=False → passed=False."""
    from generation.validator import ValidationStage

    validation = {
        "answer_correct": False,
        "textbook_aligned": True,
        "original": True,
        "bloom_accurate": True,
        "grammar_quality": True,
        "passed": False,
        "feedback": "Correct answer should be C, not A",
    }

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value=json.dumps(validation))

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.3}]

    stage = ValidationStage(
        gemini=mock_gemini, embedding=mock_embedding,
        qdrant=mock_qdrant, similarity_threshold=0.85,
    )

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question,
        textbook_context=[{"payload": {"text_content": "Content"}}],
        bloom_level="Apply and Analyze",
    )

    assert result["passed"] is False
    assert result["answer_correct"] is False


@pytest.mark.asyncio
async def test_validator_no_similar_results():
    """When Qdrant returns empty results, similarity is 0 → proceed to LLM."""
    from generation.validator import ValidationStage

    validation = {
        "answer_correct": True,
        "textbook_aligned": True,
        "original": True,
        "bloom_accurate": True,
        "grammar_quality": True,
        "passed": True,
        "feedback": "OK",
    }

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value=json.dumps(validation))

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = []  # no results

    stage = ValidationStage(
        gemini=mock_gemini, embedding=mock_embedding,
        qdrant=mock_qdrant, similarity_threshold=0.85,
    )

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question,
        textbook_context=[{"payload": {"text_content": "C"}}],
        bloom_level="Remember and Understand",
    )

    assert result["passed"] is True
    assert result["similarity_score"] == 0.0


@pytest.mark.asyncio
async def test_validator_formats_prompt_correctly():
    """Verify VALIDATION_PROMPT is formatted with question, context, bloom_level."""
    from generation.validator import ValidationStage

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value='{"answer_correct":true,"textbook_aligned":true,"original":true,"bloom_accurate":true,"grammar_quality":true,"passed":true,"feedback":"OK"}')

    mock_embedding = MagicMock()
    mock_embedding.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.2}]

    stage = ValidationStage(
        gemini=mock_gemini, embedding=mock_embedding,
        qdrant=mock_qdrant, similarity_threshold=0.85,
    )

    question = {"question_text": "Sual?", "correct_answer": "B"}
    await stage.validate(
        question=question,
        textbook_context=[{"payload": {"text_content": "Dərslik məzmunu"}}],
        bloom_level="Evaluate and Create",
    )

    # Check that generate_json was called with a prompt containing our data
    prompt_arg = mock_gemini.generate_json.call_args[0][0]
    assert "Sual?" in prompt_arg
    assert "Dərslik məzmunu" in prompt_arg
    assert "Evaluate and Create" in prompt_arg