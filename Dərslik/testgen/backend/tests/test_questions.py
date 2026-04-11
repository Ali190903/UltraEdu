"""Tests for Question Bank CRUD (Task 15)."""

import pytest


async def create_user_and_login(client, role="teacher"):
    """Helper: register user and return auth token."""
    email = f"{role}@test.com"
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "pass123",
        "full_name": f"Test {role.title()}",
        "role": role,
    })
    resp = await client.post("/api/auth/login", json={
        "email": email,
        "password": "pass123",
    })
    return resp.json()["access_token"]


async def create_question_via_db(client, token):
    """Helper: create a question by calling the generation endpoint with mocked pipeline."""
    from unittest.mock import MagicMock, AsyncMock
    from generation.router import get_pipeline
    from main import app

    mock_pipeline = MagicMock()
    mock_pipeline.run = AsyncMock(return_value={
        "question": {
            "question_text": "Test sualı?",
            "options": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
            "correct_answer": "A",
            "explanation": "Cavab 1-dir",
            "bloom_level": "Remember and Understand",
            "latex_content": None,
            "source_reference": "p.10",
        },
        "validation": {
            "passed": True,
            "answer_correct": True,
            "textbook_aligned": True,
            "original": True,
            "bloom_accurate": True,
            "grammar_quality": True,
            "feedback": "Good",
            "similarity_score": 0.3,
        },
        "attempts": 1,
        "timing": {"retrieval": 0.1, "generation": 0.5, "validation": 0.3, "total": 0.9},
    })
    app.dependency_overrides[get_pipeline] = lambda: mock_pipeline

    resp = await client.post("/api/generation/generate", json={
        "subject": "riyaziyyat",
        "grade": 9,
        "topic": "Tənliklər",
        "difficulty": "easy",
        "question_type": "mcq",
    }, headers={"Authorization": f"Bearer {token}"})

    app.dependency_overrides.pop(get_pipeline, None)
    return resp.json()["question_id"]


@pytest.mark.asyncio
async def test_list_questions_empty(client):
    """GET /api/questions with no questions returns empty list."""
    token = await create_user_and_login(client)
    response = await client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
        params={"subject": "riyaziyyat"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.asyncio
async def test_get_question_not_found(client):
    """GET /api/questions/:id with non-existent ID returns 404."""
    token = await create_user_and_login(client)
    response = await client.get(
        "/api/questions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_questions_with_data(client):
    """GET /api/questions returns created questions."""
    token = await create_user_and_login(client)
    await create_question_via_db(client, token)
    response = await client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["question_text"] == "Test sualı?"


@pytest.mark.asyncio
async def test_get_question_by_id(client):
    """GET /api/questions/:id returns the question."""
    token = await create_user_and_login(client)
    question_id = await create_question_via_db(client, token)
    response = await client.get(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["question_text"] == "Test sualı?"


@pytest.mark.asyncio
async def test_update_question_teacher(client):
    """PATCH /api/questions/:id by teacher updates the question."""
    token = await create_user_and_login(client, role="teacher")
    question_id = await create_question_via_db(client, token)
    response = await client.patch(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"question_text": "Yenilənmiş sual?"},
    )
    assert response.status_code == 200
    assert response.json()["question_text"] == "Yenilənmiş sual?"


@pytest.mark.asyncio
async def test_update_question_student_forbidden(client):
    """PATCH /api/questions/:id by student returns 403."""
    teacher_token = await create_user_and_login(client, role="teacher")
    question_id = await create_question_via_db(client, teacher_token)
    student_token = await create_user_and_login(client, role="student")
    response = await client.patch(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"question_text": "Hack attempt"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_question_teacher(client):
    """DELETE /api/questions/:id by teacher returns 204."""
    token = await create_user_and_login(client, role="teacher")
    question_id = await create_question_via_db(client, token)
    response = await client.delete(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    # Verify it's gone
    get_resp = await client.get(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_question_student_forbidden(client):
    """DELETE /api/questions/:id by student returns 403."""
    teacher_token = await create_user_and_login(client, role="teacher")
    question_id = await create_question_via_db(client, teacher_token)
    student_token = await create_user_and_login(client, role="student")
    response = await client.delete(
        f"/api/questions/{question_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_questions_filter_by_subject(client):
    """GET /api/questions?subject=X filters correctly."""
    token = await create_user_and_login(client)
    await create_question_via_db(client, token)
    # Filter by non-matching subject
    response = await client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
        params={"subject": "ingilis"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_list_questions_requires_auth(client):
    """GET /api/questions without token returns 401/403."""
    response = await client.get("/api/questions")
    assert response.status_code in (401, 403)