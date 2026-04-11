import pytest


async def get_teacher_token(client):
    await client.post("/api/auth/register", json={
        "email": "varteacher@test.com",
        "password": "pass123",
        "full_name": "VarTeacher",
        "role": "teacher",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "varteacher@test.com",
        "password": "pass123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_variants_empty(client):
    token = await get_teacher_token(client)
    response = await client.get(
        "/api/variants",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []