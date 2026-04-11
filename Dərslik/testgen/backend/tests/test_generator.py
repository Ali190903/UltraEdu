"""Tests for generation stage (Task 13 — Stage 2)."""

import json

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_generator_produces_question():
    """Stage 2: Gemini generates structured JSON question from prompt."""
    from generation.generator import GenerationStage

    generated = {
        "question_text": "Hansı ədəd tək ədəddir?",
        "options": {"A": "2", "B": "3", "C": "4", "D": "6", "E": "8"},
        "correct_answer": "B",
        "explanation": "3 tək ədəddir",
        "bloom_level": "Remember and Understand",
        "latex_content": None,
        "source_reference": "Textbook p.5-10",
    }

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value=json.dumps(generated))

    stage = GenerationStage(gemini=mock_gemini)
    result = await stage.generate(
        subject="riyaziyyat",
        grade=9,
        topic="Tənliklər",
        difficulty="easy",
        question_type="mcq",
        textbook_context=[{"payload": {"text_content": "Content", "pages": "5-10"}}],
        dim_examples=[{"payload": {"question_text": "Q?", "options": {}, "correct_answer": "A"}}],
    )

    assert result["question_text"] == "Hansı ədəd tək ədəddir?"
    assert result["correct_answer"] == "B"
    assert result["options"]["B"] == "3"


@pytest.mark.asyncio
async def test_generator_passes_system_prompt():
    """Verify SYSTEM_PROMPT is passed as system_instruction to Gemini."""
    from generation.generator import GenerationStage
    from generation.prompts import SYSTEM_PROMPT

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value='{"question_text":"Q","correct_answer":"A","explanation":"E","bloom_level":"B","source_reference":"S"}')

    stage = GenerationStage(gemini=mock_gemini)
    await stage.generate(
        subject="az_dili", grade=9, topic="Fonetika", difficulty="easy",
        question_type="mcq",
        textbook_context=[{"payload": {"text_content": "T", "pages": "1"}}],
        dim_examples=[],
    )

    call_kwargs = mock_gemini.generate_json.call_args.kwargs
    assert call_kwargs["system_instruction"] == SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_generator_handles_matching_type():
    """Matching question type should produce matching_pairs in output."""
    from generation.generator import GenerationStage

    generated = {
        "question_text": "Uyğunlaşdırın",
        "options": None,
        "matching_pairs": {"1": "A", "2": "B"},
        "correct_answer": "1-A, 2-B",
        "explanation": "Test",
        "bloom_level": "Apply and Analyze",
        "latex_content": None,
        "source_reference": "p.20",
    }

    mock_gemini = MagicMock()
    mock_gemini.generate_json = AsyncMock(return_value=json.dumps(generated))

    stage = GenerationStage(gemini=mock_gemini)
    result = await stage.generate(
        subject="riyaziyyat", grade=10, topic="Funksiyalar", difficulty="medium",
        question_type="matching",
        textbook_context=[{"payload": {"text_content": "F", "pages": "20"}}],
        dim_examples=[],
    )

    assert result["matching_pairs"] == {"1": "A", "2": "B"}
