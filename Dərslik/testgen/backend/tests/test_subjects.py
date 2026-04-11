import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.topic import Topic


@pytest.mark.asyncio
async def test_list_subjects(client):
    response = await client.get("/api/subjects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    ids = [s["id"] for s in data]
    assert "az_dili" in ids
    assert "riyaziyyat" in ids
    assert "ingilis" in ids
    for s in data:
        assert "name" in s
        assert "name_az" in s


@pytest.mark.asyncio
async def test_get_topics_empty(client):
    response = await client.get("/api/subjects/riyaziyyat/topics?grade=9")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_topics_with_data(client, engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        t1 = Topic(
            subject="riyaziyyat", grade=9, chapter="Ədədlər", chapter_order=1,
            topic="Natural ədədlər", subtopic=None, page_start=10, page_end=20,
        )
        t2 = Topic(
            subject="riyaziyyat", grade=9, chapter="Ədədlər", chapter_order=1,
            topic="Tam ədədlər", subtopic="Mənfi ədədlər", page_start=21, page_end=30,
        )
        t3 = Topic(
            subject="riyaziyyat", grade=10, chapter="Funksiyalar", chapter_order=2,
            topic="Xətti funksiya", subtopic=None, page_start=50, page_end=60,
        )
        session.add_all([t1, t2, t3])
        await session.commit()

    response = await client.get("/api/subjects/riyaziyyat/topics?grade=9")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    topics = [d["topic"] for d in data]
    assert "Natural ədədlər" in topics
    assert "Tam ədədlər" in topics


@pytest.mark.asyncio
async def test_get_topics_different_subject(client, engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        t = Topic(
            subject="az_dili", grade=9, chapter="Fonetika", chapter_order=1,
            topic="Səslər", subtopic=None, page_start=5, page_end=15,
        )
        session.add(t)
        await session.commit()

    response = await client.get("/api/subjects/riyaziyyat/topics?grade=9")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.get("/api/subjects/az_dili/topics?grade=9")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_topics_requires_grade(client):
    response = await client.get("/api/subjects/riyaziyyat/topics")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_topics_grade_validation(client):
    response = await client.get("/api/subjects/riyaziyyat/topics?grade=8")
    assert response.status_code == 422

    response = await client.get("/api/subjects/riyaziyyat/topics?grade=12")
    assert response.status_code == 422