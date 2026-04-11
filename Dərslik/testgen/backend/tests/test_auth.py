import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
        "full_name": "Test User",
        "role": "student",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "student"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "dupe@example.com",
        "password": "securepass123",
        "full_name": "Dupe User",
        "role": "student",
    }
    await client.post("/api/auth/register", json=payload)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_returns_token(client):
    await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "securepass123",
        "full_name": "Login User",
        "role": "student",
    })
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "password": "securepass123",
        "full_name": "Wrong User",
        "role": "student",
    })
    response = await client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "badpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_with_token(client):
    await client.post("/api/auth/register", json={
        "email": "me@example.com",
        "password": "securepass123",
        "full_name": "Me User",
        "role": "teacher",
    })
    login_resp = await client.post("/api/auth/login", json={
        "email": "me@example.com",
        "password": "securepass123",
    })
    token = login_resp.json()["access_token"]
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
    assert response.json()["role"] == "teacher"