"""Tests for generation schemas, prompts (Task 11), and pipeline orchestrator (Task 14)."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from generation.schemas import GenerateRequest, GeneratedQuestion, ValidationResult
from generation.prompts import BLOOM_MAP, SYSTEM_PROMPT, VALIDATION_PROMPT, build_generation_prompt


# --- Schema Tests ---


class TestGenerateRequest:
    def test_valid_request(self):
        req = GenerateRequest(
            subject="Riyaziyyat",
            grade=11,
            topic="Triqonometriya",
            difficulty="medium",
            question_type="mcq",
        )
        assert req.subject == "Riyaziyyat"
        assert req.grade == 11
        assert req.difficulty == "medium"
        assert req.question_type == "mcq"

    def test_default_question_type(self):
        req = GenerateRequest(
            subject="Az dili", grade=9, topic="Fonetika", difficulty="easy"
        )
        assert req.question_type == "mcq"


class TestGeneratedQuestion:
    def test_mcq_question(self):
        q = GeneratedQuestion(
            question_text="Hansı söz kök və şəkilçidən ibarətdir?",
            options={"A": "göz", "B": "gözlük", "C": "at", "D": "ev", "E": "su"},
            correct_answer="B",
            explanation="Gözlük sözü göz kökü və -lük şəkilçisindən ibarətdir.",
            bloom_level="Remember and Understand",
            source_reference="Azərbaycan dili 9, səh. 15",
        )
        assert q.options is not None
        assert q.matching_pairs is None
        assert q.latex_content is None

    def test_matching_question(self):
        q = GeneratedQuestion(
            question_text="Müvafiq cütləri uyğunlaşdırın",
            matching_pairs={"1": "A", "2": "B", "3": "C"},
            correct_answer="1-A, 2-B, 3-C",
            explanation="Test explanation",
            bloom_level="Apply and Analyze",
            source_reference="Riyaziyyat 10, səh. 42",
        )
        assert q.matching_pairs is not None
        assert q.options is None


class TestValidationResult:
    def test_all_pass(self):
        v = ValidationResult(
            answer_correct=True,
            textbook_aligned=True,
            original=True,
            bloom_accurate=True,
            grammar_quality=True,
            passed=True,
            feedback="All criteria met.",
        )
        assert v.passed is True

    def test_partial_fail(self):
        v = ValidationResult(
            answer_correct=True,
            textbook_aligned=True,
            original=False,
            bloom_accurate=True,
            grammar_quality=True,
            passed=False,
            feedback="Question too similar to existing DIM question.",
        )
        assert v.passed is False
        assert v.original is False


# --- Prompt Tests ---


class TestBloomMap:
    def test_all_difficulties_mapped(self):
        assert "easy" in BLOOM_MAP
        assert "medium" in BLOOM_MAP
        assert "hard" in BLOOM_MAP

    def test_bloom_levels_match_spec(self):
        """Spec §7.2: Easy=Remember+Understand, Medium=Apply+Analyze, Hard=Evaluate+Create."""
        assert "Remember" in BLOOM_MAP["easy"] and "Understand" in BLOOM_MAP["easy"]
        assert "Apply" in BLOOM_MAP["medium"] and "Analyze" in BLOOM_MAP["medium"]
        assert "Evaluate" in BLOOM_MAP["hard"] and "Create" in BLOOM_MAP["hard"]


class TestSystemPrompt:
    def test_contains_key_elements(self):
        assert "DIM" in SYSTEM_PROMPT
        assert "Bloom" in SYSTEM_PROMPT
        assert "ORIGINAL" in SYSTEM_PROMPT
        assert "Azerbaijani" in SYSTEM_PROMPT


class TestBuildGenerationPrompt:
    def test_prompt_structure(self):
        textbook_context = [
            {"payload": {"text_content": "Triqonometrik funksiyalar...", "pages": "45-47"}}
        ]
        dim_examples = [
            {
                "payload": {
                    "question_text": "sin(30°) neçədir?",
                    "options": "A: 0.5, B: 1",
                    "correct_answer": "A",
                }
            }
        ]
        prompt = build_generation_prompt(
            subject="Riyaziyyat",
            grade=11,
            topic="Triqonometriya",
            difficulty="medium",
            question_type="mcq",
            textbook_context=textbook_context,
            dim_examples=dim_examples,
        )
        assert "Riyaziyyat" in prompt
        assert "Triqonometriya" in prompt
        assert "Apply and Analyze" in prompt
        assert "Triqonometrik funksiyalar" in prompt
        assert "sin(30°)" in prompt
        assert "multiple-choice" in prompt

    def test_matching_type_instructions(self):
        prompt = build_generation_prompt(
            subject="Az dili",
            grade=9,
            topic="Fonetika",
            difficulty="easy",
            question_type="matching",
            textbook_context=[{"payload": {"text_content": "Saitlər...", "pages": "10"}}],
            dim_examples=[],
        )
        assert "matching" in prompt.lower()

    def test_open_ended_type_instructions(self):
        prompt = build_generation_prompt(
            subject="English",
            grade=11,
            topic="Grammar",
            difficulty="hard",
            question_type="open_ended",
            textbook_context=[{"payload": {"text_content": "Tenses...", "pages": "22"}}],
            dim_examples=[],
        )
        assert "open-ended" in prompt.lower()


class TestValidationPrompt:
    def test_contains_placeholders(self):
        assert "{question_json}" in VALIDATION_PROMPT
        assert "{textbook_context}" in VALIDATION_PROMPT
        assert "{bloom_level}" in VALIDATION_PROMPT

    def test_contains_five_criteria(self):
        """Spec §7.1 Stage 3B: 5 criteria."""
        assert "answer_correct" in VALIDATION_PROMPT
        assert "textbook_aligned" in VALIDATION_PROMPT
        assert "original" in VALIDATION_PROMPT
        assert "bloom_accurate" in VALIDATION_PROMPT
        assert "grammar_quality" in VALIDATION_PROMPT


# --- Pipeline Orchestrator Tests (Task 14) ---


def _make_pipeline(
    validation_results=None,
    generated_question=None,
    max_attempts=3,
):
    """Helper to build a GenerationPipeline with mocked stages."""
    from generation.pipeline import GenerationPipeline

    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value={
        "textbook_context": [{"payload": {"text_content": "Content", "pages": "5"}}],
        "dim_examples": [{"payload": {"question_text": "Q?", "options": {}, "correct_answer": "A"}}],
    })

    question = generated_question or {
        "question_text": "New question?",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "correct_answer": "A",
        "explanation": "Because...",
        "bloom_level": "Remember and Understand",
        "latex_content": None,
        "source_reference": "p.5",
    }

    mock_generator = MagicMock()
    mock_generator.generate = AsyncMock(return_value=question)

    if validation_results is None:
        validation_results = [{
            "passed": True,
            "answer_correct": True,
            "textbook_aligned": True,
            "original": True,
            "bloom_accurate": True,
            "grammar_quality": True,
            "feedback": "Good",
            "similarity_score": 0.3,
        }]

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(side_effect=validation_results)

    pipeline = GenerationPipeline(
        retrieval=mock_retrieval,
        generator=mock_generator,
        validator=mock_validator,
        max_attempts=max_attempts,
    )
    return pipeline, mock_retrieval, mock_generator, mock_validator


@pytest.mark.asyncio
async def test_pipeline_orchestrates_three_stages():
    """Spec §7.1: Pipeline runs retrieval → generation → validation, returns result."""
    pipeline, mock_retrieval, mock_generator, mock_validator = _make_pipeline()

    result = await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    assert result["question"]["question_text"] == "New question?"
    assert result["validation"]["passed"] is True
    assert result["attempts"] == 1
    mock_retrieval.retrieve.assert_awaited_once()
    mock_generator.generate.assert_awaited_once()
    mock_validator.validate.assert_awaited_once()


@pytest.mark.asyncio
async def test_pipeline_retries_on_validation_failure():
    """Spec §7.1: FAIL → retry Stage 2 (max 3 attempts)."""
    fail = {
        "passed": False, "answer_correct": False, "textbook_aligned": True,
        "original": True, "bloom_accurate": True, "grammar_quality": True,
        "feedback": "Wrong answer", "similarity_score": 0.2,
    }
    success = {
        "passed": True, "answer_correct": True, "textbook_aligned": True,
        "original": True, "bloom_accurate": True, "grammar_quality": True,
        "feedback": "Good", "similarity_score": 0.2,
    }
    pipeline, _, mock_generator, _ = _make_pipeline(
        validation_results=[fail, success],
    )

    result = await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    assert result["validation"]["passed"] is True
    assert result["attempts"] == 2
    assert mock_generator.generate.await_count == 2


@pytest.mark.asyncio
async def test_pipeline_returns_failure_after_max_attempts():
    """All attempts fail → return last result with passed=False."""
    fail = {
        "passed": False, "answer_correct": False, "textbook_aligned": True,
        "original": True, "bloom_accurate": True, "grammar_quality": True,
        "feedback": "Wrong answer", "similarity_score": 0.2,
    }
    pipeline, _, mock_generator, _ = _make_pipeline(
        validation_results=[fail, fail, fail],
        max_attempts=3,
    )

    result = await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    assert result["validation"]["passed"] is False
    assert result["attempts"] == 3
    assert mock_generator.generate.await_count == 3


@pytest.mark.asyncio
async def test_pipeline_retrieval_called_once_even_on_retry():
    """Stage 1 runs once; only Stage 2+3 retry."""
    fail = {
        "passed": False, "answer_correct": False, "textbook_aligned": True,
        "original": True, "bloom_accurate": True, "grammar_quality": True,
        "feedback": "Bad", "similarity_score": 0.1,
    }
    success = {
        "passed": True, "answer_correct": True, "textbook_aligned": True,
        "original": True, "bloom_accurate": True, "grammar_quality": True,
        "feedback": "OK", "similarity_score": 0.1,
    }
    pipeline, mock_retrieval, _, _ = _make_pipeline(
        validation_results=[fail, fail, success],
    )

    result = await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    # Retrieval only once, regardless of retries
    mock_retrieval.retrieve.assert_awaited_once()
    assert result["attempts"] == 3


@pytest.mark.asyncio
async def test_pipeline_includes_timing():
    """Pipeline result includes timing breakdown (spec §8: generation_logs)."""
    pipeline, _, _, _ = _make_pipeline()

    result = await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    assert "timing" in result
    timing = result["timing"]
    assert "retrieval" in timing
    assert "generation" in timing
    assert "validation" in timing
    assert "total" in timing
    assert all(isinstance(v, float) for v in timing.values())


@pytest.mark.asyncio
async def test_pipeline_passes_bloom_level_to_validator():
    """Difficulty 'easy' maps to 'Remember and Understand' for validation."""
    pipeline, _, _, mock_validator = _make_pipeline()

    await pipeline.run(
        subject="riyaziyyat", grade=9, topic="Tənliklər",
        difficulty="easy", question_type="mcq",
    )

    call_kwargs = mock_validator.validate.call_args.kwargs
    assert call_kwargs["bloom_level"] == "Remember and Understand"


# --- Generation Router Tests (Task 14) ---


async def _register_and_login(client):
    """Helper: register user and return auth header."""
    await client.post("/api/auth/register", json={
        "email": "gen@test.com",
        "password": "pass123",
        "full_name": "Gen User",
        "role": "student",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "gen@test.com",
        "password": "pass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _mock_pipeline_result(passed=True):
    """Build a mock pipeline run result."""
    return {
        "question": {
            "question_text": "Hansı ədəd tək ədəddir?",
            "options": {"A": "2", "B": "3", "C": "4", "D": "6", "E": "8"},
            "correct_answer": "B",
            "explanation": "3 tək ədəddir",
            "bloom_level": "Remember and Understand",
            "latex_content": None,
            "source_reference": "p.5",
        },
        "validation": {
            "passed": passed,
            "answer_correct": passed,
            "textbook_aligned": True,
            "original": True,
            "bloom_accurate": True,
            "grammar_quality": True,
            "feedback": "Good" if passed else "Wrong answer",
            "similarity_score": 0.3,
        },
        "attempts": 1,
        "timing": {
            "retrieval": 0.1,
            "generation": 0.5,
            "validation": 0.3,
            "total": 0.9,
        },
    }


@pytest.mark.asyncio
async def test_generate_endpoint_success(client):
    """POST /api/generation/generate → 200 with question data."""
    from generation.router import get_pipeline
    from main import app

    mock_pipeline = MagicMock()
    mock_pipeline.run = AsyncMock(return_value=_mock_pipeline_result(passed=True))
    app.dependency_overrides[get_pipeline] = lambda: mock_pipeline

    headers = await _register_and_login(client)
    resp = await client.post("/api/generation/generate", json={
        "subject": "riyaziyyat",
        "grade": 9,
        "topic": "Tənliklər",
        "difficulty": "easy",
        "question_type": "mcq",
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "question_id" in data
    assert data["question"]["question_text"] == "Hansı ədəd tək ədəddir?"
    assert data["attempts"] == 1

    app.dependency_overrides.pop(get_pipeline, None)


@pytest.mark.asyncio
async def test_generate_endpoint_failure_returns_422(client):
    """All attempts fail → 422 error."""
    from generation.router import get_pipeline
    from main import app

    mock_pipeline = MagicMock()
    mock_pipeline.run = AsyncMock(return_value=_mock_pipeline_result(passed=False))
    app.dependency_overrides[get_pipeline] = lambda: mock_pipeline

    headers = await _register_and_login(client)
    resp = await client.post("/api/generation/generate", json={
        "subject": "riyaziyyat",
        "grade": 9,
        "topic": "Tənliklər",
        "difficulty": "easy",
        "question_type": "mcq",
    }, headers=headers)

    assert resp.status_code == 422

    app.dependency_overrides.pop(get_pipeline, None)


@pytest.mark.asyncio
async def test_generate_endpoint_requires_auth(client):
    """No token → 403."""
    resp = await client.post("/api/generation/generate", json={
        "subject": "riyaziyyat",
        "grade": 9,
        "topic": "Tənliklər",
        "difficulty": "easy",
    })

    assert resp.status_code in (401, 403)