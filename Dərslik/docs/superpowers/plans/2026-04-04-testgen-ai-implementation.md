# TestGen AI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a RAG-based web application that generates unique, curriculum-grounded test questions for Azerbaijan's DIM university entrance exams (grades 9-11, subjects: Az dili, Math, English).

**Architecture:** Three-stage RAG pipeline (Retrieve textbook context + DIM examples → Generate via Gemini 3 Flash → Validate originality + correctness). FastAPI backend with PostgreSQL + Qdrant. Next.js frontend with student/teacher roles. Data pipeline runs locally as CLI.

**Tech Stack:** Python 3.12, FastAPI 0.135, SQLAlchemy 2.0 (async), Alembic, Qdrant 1.17, google-genai SDK 1.68, Next.js 16, React 19, Tailwind CSS 4, PostgreSQL 16, Docker Compose, KaTeX.

**Spec:** `docs/superpowers/specs/2026-04-04-testgen-ai-design.md`

---

## File Structure Map

```
testgen/
├── docker-compose.yml
├── .env.example
├── .env                          ← git-ignored
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── main.py                   ← FastAPI app entry
│   ├── config.py                 ← Settings from env vars
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py               ← SQLAlchemy Base
│   │   ├── user.py
│   │   ├── question.py
│   │   ├── variant.py
│   │   ├── report.py
│   │   ├── generation_log.py
│   │   └── topic.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── questions/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── pipeline.py           ← 3-stage orchestrator
│   │   ├── retrieval.py          ← Stage 1
│   │   ├── generator.py          ← Stage 2
│   │   ├── validator.py          ← Stage 3
│   │   ├── prompts.py            ← All LLM prompts
│   │   └── schemas.py
│   ├── variants/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── export.py
│   │   └── schemas.py
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── subjects/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── schemas.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py           ← Async SQLAlchemy engine + session
│   │   ├── qdrant.py             ← Qdrant client wrapper
│   │   ├── gemini.py             ← Gemini LLM + embedding wrapper
│   │   └── dependencies.py       ← FastAPI dependency injection
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py
│   │   ├── toc_extractor.py
│   │   ├── chunker.py
│   │   ├── dim_parser.py
│   │   ├── indexer.py
│   │   └── run_pipeline.py       ← CLI entry
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_generation.py
│       ├── test_questions.py
│       ├── test_variants.py
│       ├── test_data_pipeline.py
│       └── test_retrieval.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              ← Landing
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── generate/page.tsx     ← Student generate
│   │   │   ├── teacher/
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── generate/page.tsx ← Bulk generation
│   │   │   │   ├── bank/page.tsx
│   │   │   │   ├── reports/page.tsx
│   │   │   │   └── export/page.tsx
│   │   ├── components/
│   │   │   ├── QuestionCard.tsx
│   │   │   ├── GenerateForm.tsx
│   │   │   ├── TopicSelector.tsx
│   │   │   ├── DifficultyPicker.tsx
│   │   │   ├── VariantBuilder.tsx
│   │   │   ├── QuestionEditor.tsx
│   │   │   ├── ReportButton.tsx
│   │   │   ├── ExportDialog.tsx
│   │   │   ├── LatexRenderer.tsx
│   │   │   └── Navbar.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── types.ts
│   │   └── styles/
│   │       └── globals.css
│
└── data/                             ← git-ignored, symlinked or configured via env
    ├── textbooks/
    └── dim_tests/
```

## Prerequisites

Before starting, ensure these are installed:
- Docker + Docker Compose
- Python 3.12+
- Node.js 20+
- A Gemini API key (from Google AI Studio)

---

## Phase 1: Project Foundation

### Task 1: Monorepo Scaffolding

**Files:**
- Create: `testgen/docker-compose.yml`
- Create: `testgen/.env.example`
- Create: `testgen/.gitignore`
- Create: `testgen/backend/Dockerfile`
- Create: `testgen/backend/requirements.txt`
- Create: `testgen/frontend/Dockerfile`
- Create: `testgen/frontend/package.json`

- [ ] **Step 1: Initialize git repo and create root files**

```bash
cd "C:/Users/User/Desktop/Dərslik"
mkdir -p testgen && cd testgen
git init
```

Create `testgen/.gitignore`:

```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Node
node_modules/
.next/
out/

# Environment
.env
.env.local

# Data (PDFs are large, not committed)
data/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Docker
*.log
```

Create `testgen/.env.example`:

```env
# Gemini
GEMINI_API_KEY=your-gemini-api-key

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://testgen:testgen@db:5432/testgen
DATABASE_URL_SYNC=postgresql://testgen:testgen@db:5432/testgen

# Qdrant
QDRANT_URL=http://qdrant:6333

# Auth
JWT_SECRET=change-this-to-a-random-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Google OAuth (optional for MVP)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Generation
SIMILARITY_THRESHOLD=0.85
MAX_GENERATION_ATTEMPTS=3

# Data Pipeline (local paths, not used in Docker)
TEXTBOOK_DIR=../sinif9,../sinif10,../sinif11
DIM_TEST_DIR=../data/dim_tests
```

- [ ] **Step 2: Create Docker Compose**

Create `testgen/docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: testgen
      POSTGRES_PASSWORD: testgen
      POSTGRES_DB: testgen
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testgen"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    command: npm run dev

volumes:
  pgdata:
  qdrant_data:
```

- [ ] **Step 3: Create backend Dockerfile and requirements**

Create `testgen/backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `testgen/backend/requirements.txt`:

```
fastapi==0.135.3
uvicorn[standard]==0.34.0
sqlalchemy[asyncio]==2.0.49
asyncpg==0.30.0
alembic==1.14.1
pydantic==2.10.4
pydantic-settings==2.7.1
PyJWT[crypto]==2.10.1
bcrypt==4.3.0
email-validator==2.2.0
python-multipart==0.0.20
httpx==0.28.1
google-genai==1.68.0
qdrant-client==1.17.1
python-dotenv==1.0.1
pytest==8.3.4
pytest-asyncio==0.24.0
```

- [ ] **Step 4: Create frontend Dockerfile and package.json**

Create `testgen/frontend/package.json`:

```json
{
  "name": "testgen-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "16.2.0",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "katex": "^0.16.11"
  },
  "devDependencies": {
    "@types/node": "^22",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@types/katex": "^0.16.7",
    "@tailwindcss/postcss": "^4.1.0",
    "tailwindcss": "^4.1.0",
    "typescript": "^5"
  }
}
```

Create `testgen/frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
```

- [ ] **Step 5: Verify Docker Compose starts**

```bash
cd testgen
cp .env.example .env
docker compose up db qdrant -d
```

Expected: Both `db` and `qdrant` containers start and pass health checks.

```bash
docker compose ps
```

Expected: Both services show "healthy" status.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: project scaffolding with Docker Compose, backend/frontend structure"
```

---

### Task 2: PostgreSQL Models & Migrations

**Files:**
- Create: `testgen/backend/models/base.py`
- Create: `testgen/backend/models/__init__.py`
- Create: `testgen/backend/models/user.py`
- Create: `testgen/backend/models/question.py`
- Create: `testgen/backend/models/variant.py`
- Create: `testgen/backend/models/report.py`
- Create: `testgen/backend/models/generation_log.py`
- Create: `testgen/backend/models/topic.py`
- Create: `testgen/backend/core/__init__.py`
- Create: `testgen/backend/core/database.py`
- Create: `testgen/backend/config.py`
- Create: `testgen/backend/alembic.ini`
- Create: `testgen/backend/alembic/env.py`

- [ ] **Step 1: Create config module**

Create `testgen/backend/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://testgen:testgen@db:5432/testgen"
    database_url_sync: str = "postgresql://testgen:testgen@db:5432/testgen"
    qdrant_url: str = "http://qdrant:6333"
    gemini_api_key: str = ""
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    google_client_id: str = ""
    google_client_secret: str = ""
    similarity_threshold: float = 0.85
    max_generation_attempts: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 2: Create database connection**

Create `testgen/backend/core/__init__.py` (empty file).

Create `testgen/backend/core/database.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

- [ ] **Step 3: Create SQLAlchemy base and all models**

Create `testgen/backend/models/base.py`:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Create `testgen/backend/models/user.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    auth_provider: Mapped[str] = mapped_column(String(20), nullable=False, default="email")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Create `testgen/backend/models/question.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)  # mcq/matching/open_ended
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)  # easy/medium/hard
    bloom_level: Mapped[str] = mapped_column(String(30), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    matching_pairs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    latex_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    validation_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    times_served: Mapped[int] = mapped_column(Integer, default=0)
    report_count: Mapped[int] = mapped_column(Integer, default=0)
```

Create `testgen/backend/models/variant.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_dist: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VariantQuestion(Base):
    __tablename__ = "variant_questions"

    variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("variants.id"), primary_key=True)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id"), primary_key=True)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
```

Create `testgen/backend/models/report.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    reported_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(30), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

Create `testgen/backend/models/generation_log.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    retrieval_time: Mapped[float] = mapped_column(Float, nullable=False)
    generation_time: Mapped[float] = mapped_column(Float, nullable=False)
    validation_time: Mapped[float] = mapped_column(Float, nullable=False)
    total_time: Mapped[float] = mapped_column(Float, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    token_usage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

Create `testgen/backend/models/topic.py`:

```python
import uuid

from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter_order: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

Create `testgen/backend/models/__init__.py`:

```python
from models.base import Base
from models.user import User
from models.question import Question
from models.variant import Variant, VariantQuestion
from models.report import Report
from models.generation_log import GenerationLog
from models.topic import Topic

__all__ = ["Base", "User", "Question", "Variant", "VariantQuestion", "Report", "GenerationLog", "Topic"]
```

- [ ] **Step 4: Set up Alembic**

Create `testgen/backend/alembic.ini`:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://testgen:testgen@localhost:5432/testgen

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `testgen/backend/alembic/env.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 5: Generate and run initial migration**

```bash
cd testgen/backend
pip install -r requirements.txt
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Expected: Migration file created in `alembic/versions/`. All 7 tables created in PostgreSQL.

Verify:

```bash
docker compose exec db psql -U testgen -c "\dt"
```

Expected output lists: `users`, `questions`, `variants`, `variant_questions`, `reports`, `generation_logs`, `topics`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: PostgreSQL models and Alembic migrations for all 7 tables"
```

---

### Task 3: FastAPI Application Shell

**Files:**
- Create: `testgen/backend/main.py`
- Create: `testgen/backend/core/dependencies.py`
- Create: `testgen/backend/tests/__init__.py`
- Create: `testgen/backend/tests/conftest.py`
- Test: `testgen/backend/tests/test_health.py`

- [ ] **Step 1: Write failing test for health endpoint**

Create `testgen/backend/tests/__init__.py` (empty file).

Create `testgen/backend/tests/conftest.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

Create `testgen/backend/tests/test_health.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd testgen/backend
pytest tests/test_health.py -v
```

Expected: FAIL — `main` module not found.

- [ ] **Step 3: Create FastAPI app**

Create `testgen/backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TestGen AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

Create `testgen/backend/core/dependencies.py`:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_health.py -v
```

Expected: PASS.

- [ ] **Step 5: Verify Docker backend starts**

```bash
cd testgen
docker compose up backend -d
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: FastAPI app shell with health endpoint and test infrastructure"
```

---

## Phase 2: Authentication & Core Clients

### Task 4: Auth System (JWT + Register + Login)

**Files:**
- Create: `testgen/backend/auth/__init__.py`
- Create: `testgen/backend/auth/schemas.py`
- Create: `testgen/backend/auth/security.py`
- Create: `testgen/backend/auth/service.py`
- Create: `testgen/backend/auth/router.py`
- Modify: `testgen/backend/main.py`
- Test: `testgen/backend/tests/test_auth.py`

- [ ] **Step 1: Write failing tests for auth**

Create `testgen/backend/tests/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_auth.py -v
```

Expected: FAIL — auth modules not found.

- [ ] **Step 3: Create auth schemas**

Create `testgen/backend/auth/__init__.py` (empty file).

Create `testgen/backend/auth/schemas.py`:

```python
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 4: Create security utilities**

Create `testgen/backend/auth/security.py`:

```python
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.database import get_db
from models.user import User

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 5: Create auth service**

Create `testgen/backend/auth/service.py`:

```python
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from auth.security import hash_password, verify_password, create_access_token
from auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse


async def register_user(db: AsyncSession, req: RegisterRequest) -> UserResponse:
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        return None  # duplicate

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        auth_provider="email",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def login_user(db: AsyncSession, req: LoginRequest) -> TokenResponse | None:
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        return None

    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
```

- [ ] **Step 6: Create auth router and wire to app**

Create `testgen/backend/auth/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth.service import register_user, login_user
from auth.security import get_current_user
from models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, req)
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await login_user(db, req)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
```

Add router to `testgen/backend/main.py` — append after the health endpoint:

```python
from auth.router import router as auth_router

app.include_router(auth_router)
```

- [ ] **Step 7: Update test conftest for database isolation**

Replace `testgen/backend/tests/conftest.py`:

```python
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings
from models.base import Base
from core.database import get_db
from main import app

# Use a separate test database — never test against the development/production DB
TEST_DATABASE_URL = settings.database_url.replace("/testgen", "/testgen_test")
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
pytest tests/test_auth.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: auth system with JWT registration, login, and /me endpoint"
```

---

### Task 5: Gemini Client Wrapper

**Files:**
- Create: `testgen/backend/core/gemini.py`
- Create: `testgen/backend/core/embedding.py` (merged into gemini.py for simplicity)
- Test: `testgen/backend/tests/test_gemini.py`

- [ ] **Step 1: Write failing test for Gemini client**

Create `testgen/backend/tests/test_gemini.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_gemini_generate_text():
    from core.gemini import GeminiClient

    mock_response = MagicMock()
    mock_response.text = '{"question": "test?"}'

    with patch("core.gemini.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiClient(api_key="fake-key")
        result = await client.generate("Test prompt")
        assert result == '{"question": "test?"}'


@pytest.mark.asyncio
async def test_gemini_embed_text():
    from core.gemini import GeminiClient

    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 3072)]

    with patch("core.gemini.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.embed_content.return_value = mock_response

        client = GeminiClient(api_key="fake-key")
        result = await client.embed("Test text")
        assert len(result) == 3072
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_gemini.py -v
```

Expected: FAIL — `core.gemini` not found.

- [ ] **Step 3: Implement Gemini client**

Create `testgen/backend/core/gemini.py`:

```python
import asyncio

from google import genai
from google.genai import types

LLM_MODEL = "gemini-3-flash-preview"
EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 3072


class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        ) if system_instruction else None

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=config,
        )
        return response.text

    async def generate_json(self, prompt: str, system_instruction: str | None = None) -> str:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=system_instruction,
        )

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=config,
        )
        return response.text

    async def embed(self, text: str) -> list[float]:
        response = await self.client.aio.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_gemini.py -v
```

Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: Gemini client wrapper for LLM generation and embedding"
```

---

### Task 6: Qdrant Client & Collection Setup

**Files:**
- Create: `testgen/backend/core/qdrant.py`
- Test: `testgen/backend/tests/test_qdrant_client.py`

- [ ] **Step 1: Write failing test for Qdrant wrapper**

Create `testgen/backend/tests/test_qdrant_client.py`:

```python
import pytest
from unittest.mock import MagicMock, patch


def test_qdrant_wrapper_search():
    from core.qdrant import QdrantWrapper

    mock_client = MagicMock()
    mock_hit = MagicMock()
    mock_hit.payload = {"text_content": "sample chunk", "subject": "math"}
    mock_hit.score = 0.92
    mock_client.query_points.return_value.points = [mock_hit]

    with patch("core.qdrant.QdrantClient", return_value=mock_client):
        wrapper = QdrantWrapper(url="http://fake:6333")
        results = wrapper.search(
            collection="textbooks",
            vector=[0.1] * 3072,
            filters={"subject": "math"},
            limit=5,
        )
        assert len(results) == 1
        assert results[0]["payload"]["subject"] == "math"
        assert results[0]["score"] == 0.92


def test_qdrant_wrapper_upsert():
    from core.qdrant import QdrantWrapper

    mock_client = MagicMock()

    with patch("core.qdrant.QdrantClient", return_value=mock_client):
        wrapper = QdrantWrapper(url="http://fake:6333")
        wrapper.upsert(
            collection="textbooks",
            points=[{
                "id": "abc-123",
                "vector": [0.1] * 3072,
                "payload": {"subject": "math", "text_content": "chunk"},
            }],
        )
        mock_client.upsert.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_qdrant_client.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement Qdrant wrapper**

Create `testgen/backend/core/qdrant.py`:

```python
from qdrant_client import QdrantClient, models

TEXTBOOKS_COLLECTION = "textbooks"
DIM_TESTS_COLLECTION = "dim_tests"
VECTOR_DIM = 3072


class QdrantWrapper:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)

    def ensure_collections(self):
        for name in [TEXTBOOKS_COLLECTION, DIM_TESTS_COLLECTION]:
            collections = [c.name for c in self.client.get_collections().collections]
            if name not in collections:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=models.VectorParams(size=VECTOR_DIM, distance=models.Distance.COSINE),
                )

    def search(
        self,
        collection: str,
        vector: list[float],
        filters: dict | None = None,
        limit: int = 5,
    ) -> list[dict]:
        query_filter = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(
                    models.FieldCondition(key=key, match=models.MatchValue(value=value))
                )
            query_filter = models.Filter(must=must_conditions)

        results = self.client.query_points(
            collection_name=collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
        )
        return [
            {"payload": hit.payload, "score": hit.score}
            for hit in results.points
        ]

    def upsert(self, collection: str, points: list[dict]):
        qdrant_points = [
            models.PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"],
            )
            for p in points
        ]
        self.client.upsert(collection_name=collection, points=qdrant_points)

    def count(self, collection: str) -> int:
        return self.client.count(collection_name=collection).count
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_qdrant_client.py -v
```

Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: Qdrant wrapper with search, upsert, and collection management"
```

---

## Phase 3: Data Pipeline

### Task 7: PDF Processor

**Files:**
- Create: `testgen/backend/data_pipeline/__init__.py`
- Create: `testgen/backend/data_pipeline/pdf_processor.py`
- Test: `testgen/backend/tests/test_data_pipeline.py`

- [ ] **Step 1: Write failing test for PDF processor**

Create `testgen/backend/data_pipeline/__init__.py` (empty file).

Create `testgen/backend/tests/test_data_pipeline.py`:

```python
import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
async def test_pdf_processor_extracts_text():
    from data_pipeline.pdf_processor import PdfProcessor

    mock_gemini = MagicMock()
    mock_gemini.generate.return_value = "Page 1 content about algebra."

    with patch("data_pipeline.pdf_processor.GeminiClient", return_value=mock_gemini):
        processor = PdfProcessor(api_key="fake")
        result = await processor.extract_text("fake/path.pdf", pages=(1, 5))
        assert isinstance(result, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_data_pipeline.py::test_pdf_processor_extracts_text -v
```

Expected: FAIL.

- [ ] **Step 3: Implement PDF processor**

Create `testgen/backend/data_pipeline/pdf_processor.py`:

```python
import json
from pathlib import Path

from google import genai
from google.genai import types

LLM_MODEL = "gemini-3-flash-preview"

# Gemini API inline PDF limit is 50MB; larger files use the Files API
INLINE_PDF_LIMIT = 50 * 1024 * 1024


class PdfProcessor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _upload_if_needed(self, path: Path) -> types.Part | types.File:
        """Return an inline Part for small PDFs, or upload via Files API for large ones."""
        file_bytes = path.read_bytes()
        if len(file_bytes) <= INLINE_PDF_LIMIT:
            return types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        # Large file: upload via Files API
        uploaded = await self.client.aio.files.upload(
            file=path, config=types.UploadFileConfig(mime_type="application/pdf")
        )
        return uploaded

    async def extract_text(self, pdf_path: str, pages: tuple[int, int] | None = None) -> list[dict]:
        """Extract text content from PDF using Gemini's native PDF understanding."""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pdf_content = await self._upload_if_needed(path)

        prompt = """Extract all text content from this PDF page by page.
For each page, return the page number and the full text content.
For mathematical formulas, use LaTeX notation.
For images/diagrams, provide a text description in [IMAGE: description] format.

Return as JSON array:
[{"page": 1, "text": "...", "has_image": false, "image_description": null, "latex": null}, ...]"""

        if pages:
            prompt += f"\nOnly process pages {pages[0]} to {pages[1]}."

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[pdf_content, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)

    async def get_page_count_estimate(self, pdf_path: str) -> int:
        """Estimate page count from file size (rough: ~50KB per page for text PDFs)."""
        size_bytes = Path(pdf_path).stat().st_size
        return max(1, size_bytes // 50_000)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_data_pipeline.py::test_pdf_processor_extracts_text -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: PDF processor using Gemini native PDF parsing"
```

---

### Task 8: TOC Extractor & Chunker

**Files:**
- Create: `testgen/backend/data_pipeline/toc_extractor.py`
- Create: `testgen/backend/data_pipeline/chunker.py`
- Test: `testgen/backend/tests/test_data_pipeline.py` (append)

- [ ] **Step 1: Write failing tests**

Append to `testgen/backend/tests/test_data_pipeline.py`:

```python
@pytest.mark.asyncio
async def test_toc_extractor():
    from data_pipeline.toc_extractor import TocExtractor

    mock_gemini = MagicMock()
    mock_gemini.generate_json.return_value = '[{"chapter": "Cəbr", "chapter_order": 1, "topics": [{"topic": "Tənliklər", "subtopic": null, "page_start": 5, "page_end": 20}]}]'

    with patch("data_pipeline.toc_extractor.GeminiClient", return_value=mock_gemini):
        extractor = TocExtractor(api_key="fake")
        toc = await extractor.extract("fake/path.pdf")
        assert len(toc) == 1
        assert toc[0]["chapter"] == "Cəbr"
        assert len(toc[0]["topics"]) == 1


def test_chunker_splits_by_topic():
    from data_pipeline.chunker import Chunker

    pages = [
        {"page": 5, "text": "Tənlik nədir? " * 100, "has_image": False, "image_description": None, "latex": None},
        {"page": 6, "text": "Xətti tənliklər. " * 100, "has_image": False, "image_description": None, "latex": None},
    ]
    toc = [{"chapter": "Cəbr", "chapter_order": 1, "topics": [
        {"topic": "Tənliklər", "subtopic": None, "page_start": 5, "page_end": 6}
    ]}]

    chunker = Chunker(max_tokens=200)
    chunks = chunker.chunk(pages, toc, subject="riyaziyyat", grade=9)
    assert len(chunks) >= 1
    assert all(c["subject"] == "riyaziyyat" for c in chunks)
    assert all(c["grade"] == 9 for c in chunks)
    assert all("text_content" in c for c in chunks)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_data_pipeline.py -v
```

Expected: New tests FAIL.

- [ ] **Step 3: Implement TOC extractor**

Create `testgen/backend/data_pipeline/toc_extractor.py`:

```python
import json
from pathlib import Path

from google import genai
from google.genai import types

LLM_MODEL = "gemini-3-flash-preview"
INLINE_PDF_LIMIT = 50 * 1024 * 1024


class TocExtractor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _upload_if_needed(self, path: Path) -> types.Part | types.File:
        """Return an inline Part for small PDFs, or upload via Files API for large ones."""
        file_bytes = path.read_bytes()
        if len(file_bytes) <= INLINE_PDF_LIMIT:
            return types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        uploaded = await self.client.aio.files.upload(
            file=path, config=types.UploadFileConfig(mime_type="application/pdf")
        )
        return uploaded

    async def extract(self, pdf_path: str) -> list[dict]:
        """Extract table of contents from a textbook PDF."""
        path = Path(pdf_path)
        pdf_content = await self._upload_if_needed(path)

        prompt = """Analyze this textbook PDF and extract its table of contents.
Return a structured JSON array of chapters with their topics:
[{
  "chapter": "Chapter name",
  "chapter_order": 1,
  "topics": [
    {"topic": "Topic name", "subtopic": "Subtopic or null", "page_start": 5, "page_end": 20}
  ]
}]

Be thorough — include all chapters and topics visible in the TOC or inferable from headings."""

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[pdf_content, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
```

- [ ] **Step 4: Implement chunker**

Create `testgen/backend/data_pipeline/chunker.py`:

```python
import uuid


class Chunker:
    def __init__(self, max_tokens: int = 1000):
        self.max_tokens = max_tokens

    def chunk(
        self,
        pages: list[dict],
        toc: list[dict],
        subject: str,
        grade: int,
    ) -> list[dict]:
        """Hybrid chunking: topic-based from TOC, then size-based splits."""
        chunks = []
        page_map = {p["page"]: p for p in pages}

        for chapter in toc:
            for topic_info in chapter["topics"]:
                topic_pages = []
                start = topic_info.get("page_start", 1)
                end = topic_info.get("page_end", start)

                for pg_num in range(start, end + 1):
                    if pg_num in page_map:
                        topic_pages.append(page_map[pg_num])

                if not topic_pages:
                    continue

                full_text = " ".join(p["text"] for p in topic_pages)
                has_image = any(p.get("has_image") for p in topic_pages)
                image_desc = " ".join(
                    p["image_description"] for p in topic_pages
                    if p.get("image_description")
                ) or None
                latex = " ".join(
                    p["latex"] for p in topic_pages if p.get("latex")
                ) or None

                sub_chunks = self._split_text(full_text, self.max_tokens)

                for i, text in enumerate(sub_chunks):
                    chunks.append({
                        "id": str(uuid.uuid4()),
                        "subject": subject,
                        "grade": grade,
                        "chapter": chapter["chapter"],
                        "topic": topic_info["topic"],
                        "subtopic": topic_info.get("subtopic"),
                        "pages": f"{start}-{end}",
                        "text_content": text,
                        "has_image": has_image if i == 0 else False,
                        "image_description": image_desc if i == 0 else None,
                        "latex": latex if i == 0 else None,
                    })

        return chunks

    def _split_text(self, text: str, max_tokens: int) -> list[str]:
        """Split text into chunks of approximately max_tokens (word-based estimate)."""
        words = text.split()
        if len(words) <= max_tokens:
            return [text]

        result = []
        current = []
        count = 0

        for word in words:
            current.append(word)
            count += 1
            if count >= max_tokens:
                result.append(" ".join(current))
                current = []
                count = 0

        if current:
            result.append(" ".join(current))

        return result
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_data_pipeline.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: TOC extractor and hybrid chunker for textbook processing"
```

---

### Task 9: DIM Question Parser

**Files:**
- Create: `testgen/backend/data_pipeline/dim_parser.py`
- Test: `testgen/backend/tests/test_data_pipeline.py` (append)

- [ ] **Step 1: Write failing test**

Append to `testgen/backend/tests/test_data_pipeline.py`:

```python
@pytest.mark.asyncio
async def test_dim_parser_extracts_questions():
    from data_pipeline.dim_parser import DimParser

    sample_response = json.dumps([{
        "question_text": "Hansı söz düzgün yazılıb?",
        "options": {"A": "kitab", "B": "kitap", "C": "ketab", "D": "kiteb", "E": "ketap"},
        "correct_answer": "A",
        "topic": "Orfoqrafiya",
        "difficulty_estimated": "easy",
        "question_type": "mcq",
        "year": 2024,
        "source_type": "dim_test",
        "has_image": False,
    }])

    mock_gemini = MagicMock()
    mock_gemini.client.models.generate_content.return_value = MagicMock(text=sample_response)

    with patch("data_pipeline.dim_parser.genai") as mock_genai:
        mock_genai.Client.return_value = MagicMock()
        parser = DimParser(api_key="fake")
        parser.client = mock_gemini.client

        questions = await parser.parse("fake/dim_test.pdf", subject="az_dili")
        assert len(questions) == 1
        assert questions[0]["correct_answer"] == "A"
```

Add at top of test file if not present:

```python
import json
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_data_pipeline.py::test_dim_parser_extracts_questions -v
```

Expected: FAIL.

- [ ] **Step 3: Implement DIM parser**

Create `testgen/backend/data_pipeline/dim_parser.py`:

```python
import json
import uuid
from pathlib import Path

from google import genai
from google.genai import types

LLM_MODEL = "gemini-3-flash-preview"
INLINE_PDF_LIMIT = 50 * 1024 * 1024


class DimParser:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _upload_if_needed(self, path: Path) -> types.Part | types.File:
        """Return an inline Part for small PDFs, or upload via Files API for large ones."""
        file_bytes = path.read_bytes()
        if len(file_bytes) <= INLINE_PDF_LIMIT:
            return types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
        uploaded = await self.client.aio.files.upload(
            file=path, config=types.UploadFileConfig(mime_type="application/pdf")
        )
        return uploaded

    async def parse(self, pdf_path: str, subject: str) -> list[dict]:
        """Extract individual questions from a DIM test PDF."""
        path = Path(pdf_path)
        pdf_content = await self._upload_if_needed(path)

        prompt = f"""Extract all test questions from this DIM ({subject}) exam PDF.

For each question, return structured JSON:
[{{
  "question_text": "Full question text",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}} or null for open-ended,
  "correct_answer": "A" or the answer text,
  "topic": "Topic name in Azerbaijani",
  "difficulty_estimated": "easy|medium|hard",
  "question_type": "mcq|matching|open_ended",
  "year": 2024 or null,
  "source_type": "dim_test",
  "has_image": true/false,
  "image_description": "Description if has_image" or null
}}]

For math questions, use LaTeX notation for formulas.
Classify topics using standard DIM exam categories for {subject}."""

        response = await self.client.aio.models.generate_content(
            model=LLM_MODEL,
            contents=[pdf_content, prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )

        questions = json.loads(response.text)
        for q in questions:
            q["id"] = str(uuid.uuid4())
            q["subject"] = subject
        return questions
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_data_pipeline.py::test_dim_parser_extracts_questions -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: DIM test question parser using Gemini PDF extraction"
```

---

### Task 10: Embedding, Indexer & Pipeline CLI

**Files:**
- Create: `testgen/backend/data_pipeline/indexer.py`
- Create: `testgen/backend/data_pipeline/run_pipeline.py`
- Test: `testgen/backend/tests/test_data_pipeline.py` (append)

- [ ] **Step 1: Write failing test for indexer**

Append to `testgen/backend/tests/test_data_pipeline.py`:

```python
@pytest.mark.asyncio
async def test_indexer_indexes_chunks():
    from data_pipeline.indexer import Indexer

    mock_gemini = MagicMock()
    mock_gemini.embed.return_value = [0.1] * 3072

    mock_qdrant = MagicMock()

    indexer = Indexer(gemini=mock_gemini, qdrant=mock_qdrant)

    chunks = [{
        "id": "test-id",
        "subject": "riyaziyyat",
        "grade": 9,
        "chapter": "Cəbr",
        "topic": "Tənliklər",
        "subtopic": None,
        "pages": "5-10",
        "text_content": "Content about equations",
        "has_image": False,
        "image_description": None,
        "latex": None,
    }]

    await indexer.index_textbook_chunks(chunks)
    mock_qdrant.upsert.assert_called_once()
    call_args = mock_qdrant.upsert.call_args
    assert call_args[1]["collection"] == "textbooks"
    assert len(call_args[1]["points"]) == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_data_pipeline.py::test_indexer_indexes_chunks -v
```

Expected: FAIL.

- [ ] **Step 3: Implement indexer**

Create `testgen/backend/data_pipeline/indexer.py`:

```python
class Indexer:
    def __init__(self, gemini, qdrant):
        self.gemini = gemini
        self.qdrant = qdrant

    async def index_textbook_chunks(self, chunks: list[dict], batch_size: int = 10):
        """Embed and index textbook chunks into Qdrant."""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["text_content"] for c in batch]
            vectors = await self.gemini.embed_batch(texts)

            points = []
            for chunk, vector in zip(batch, vectors):
                payload = {k: v for k, v in chunk.items() if k not in ("id",)}
                points.append({
                    "id": chunk["id"],
                    "vector": vector,
                    "payload": payload,
                })

            self.qdrant.upsert(collection="textbooks", points=points)
            print(f"  Indexed {min(i + batch_size, len(chunks))}/{len(chunks)} textbook chunks")

    async def index_dim_questions(self, questions: list[dict], batch_size: int = 10):
        """Embed and index DIM questions into Qdrant."""
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            texts = [q["question_text"] for q in batch]
            vectors = await self.gemini.embed_batch(texts)

            points = []
            for question, vector in zip(batch, vectors):
                payload = {k: v for k, v in question.items() if k not in ("id",)}
                points.append({
                    "id": question["id"],
                    "vector": vector,
                    "payload": payload,
                })

            self.qdrant.upsert(collection="dim_tests", points=points)
            print(f"  Indexed {min(i + batch_size, len(questions))}/{len(questions)} DIM questions")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_data_pipeline.py::test_indexer_indexes_chunks -v
```

Expected: PASS.

- [ ] **Step 5: Implement pipeline CLI runner**

Create `testgen/backend/data_pipeline/run_pipeline.py`:

```python
"""
CLI entry point for the data pipeline.
Runs locally — processes PDFs and indexes to remote Qdrant.

Usage:
    python -m data_pipeline.run_pipeline --mode textbooks --subject riyaziyyat --grade 9 --pdf-path ../sinif9/Riyaziyyat.pdf
    python -m data_pipeline.run_pipeline --mode dim --subject riyaziyyat --pdf-path ../data/dim_tests/riyaziyyat/test1.pdf
    python -m data_pipeline.run_pipeline --mode all --config pipeline_config.json
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.gemini import GeminiClient
from core.qdrant import QdrantWrapper
from data_pipeline.pdf_processor import PdfProcessor
from data_pipeline.toc_extractor import TocExtractor
from data_pipeline.chunker import Chunker
from data_pipeline.dim_parser import DimParser
from data_pipeline.indexer import Indexer

SUBJECT_MAP = {
    "az_dili": "Azerbaycan_dili_tedris.pdf",
    "riyaziyyat": "Riyaziyyat.pdf",
    "ingilis": {"sinif9": "ingilis_dili.pdf", "sinif10": "ingili-dili.pdf", "sinif11": "ing_dili.pdf"},
}

GRADE_DIRS = {9: "sinif9", 10: "sinif10", 11: "sinif11"}


async def process_textbook(
    pdf_path: str,
    subject: str,
    grade: int,
    gemini: GeminiClient,
    qdrant: QdrantWrapper,
):
    print(f"\n--- Processing textbook: {subject} grade {grade} ---")
    print(f"PDF: {pdf_path}")

    processor = PdfProcessor(api_key=os.getenv("GEMINI_API_KEY"))
    toc_extractor = TocExtractor(api_key=os.getenv("GEMINI_API_KEY"))
    chunker = Chunker(max_tokens=1000)
    indexer = Indexer(gemini=gemini, qdrant=qdrant)

    print("1. Extracting TOC...")
    toc = await toc_extractor.extract(pdf_path)
    print(f"   Found {sum(len(ch['topics']) for ch in toc)} topics in {len(toc)} chapters")

    print("2. Extracting text...")
    pages = await processor.extract_text(pdf_path)
    print(f"   Extracted {len(pages)} pages")

    print("3. Chunking...")
    chunks = chunker.chunk(pages, toc, subject=subject, grade=grade)
    print(f"   Created {len(chunks)} chunks")

    print("4. Embedding & indexing...")
    await indexer.index_textbook_chunks(chunks)
    print(f"   Done! {qdrant.count('textbooks')} total chunks in textbooks collection")

    return toc


async def process_dim_tests(
    pdf_path: str,
    subject: str,
    gemini: GeminiClient,
    qdrant: QdrantWrapper,
):
    print(f"\n--- Processing DIM tests: {subject} ---")
    print(f"PDF: {pdf_path}")

    parser = DimParser(api_key=os.getenv("GEMINI_API_KEY"))
    indexer = Indexer(gemini=gemini, qdrant=qdrant)

    print("1. Parsing questions...")
    questions = await parser.parse(pdf_path, subject=subject)
    print(f"   Extracted {len(questions)} questions")

    print("2. Embedding & indexing...")
    await indexer.index_dim_questions(questions)
    print(f"   Done! {qdrant.count('dim_tests')} total questions in dim_tests collection")


async def save_topics_to_db(toc: list[dict], subject: str, grade: int):
    """Save extracted TOC to PostgreSQL topics table."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from models.topic import Topic
    from models.base import Base

    db_url = os.getenv("DATABASE_URL_SYNC", "postgresql://testgen:testgen@localhost:5432/testgen")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        for chapter in toc:
            for topic_info in chapter["topics"]:
                topic = Topic(
                    subject=subject,
                    grade=grade,
                    chapter=chapter["chapter"],
                    chapter_order=chapter["chapter_order"],
                    topic=topic_info["topic"],
                    subtopic=topic_info.get("subtopic"),
                    page_start=topic_info.get("page_start"),
                    page_end=topic_info.get("page_end"),
                )
                session.add(topic)
        session.commit()
        print(f"   Saved {sum(len(ch['topics']) for ch in toc)} topics to PostgreSQL")


async def main():
    parser = argparse.ArgumentParser(description="TestGen Data Pipeline")
    parser.add_argument("--mode", choices=["textbooks", "dim", "all"], required=True)
    parser.add_argument("--subject", type=str, help="Subject: az_dili, riyaziyyat, ingilis")
    parser.add_argument("--grade", type=int, help="Grade: 9, 10, 11")
    parser.add_argument("--pdf-path", type=str, help="Path to PDF file")
    parser.add_argument("--qdrant-url", type=str, default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    gemini = GeminiClient(api_key=api_key)
    qdrant = QdrantWrapper(url=args.qdrant_url)
    qdrant.ensure_collections()

    if args.mode == "textbooks" and args.pdf_path:
        toc = await process_textbook(args.pdf_path, args.subject, args.grade, gemini, qdrant)
        await save_topics_to_db(toc, args.subject, args.grade)

    elif args.mode == "dim" and args.pdf_path:
        await process_dim_tests(args.pdf_path, args.subject, gemini, qdrant)

    elif args.mode == "all":
        base_dir = Path(__file__).resolve().parent.parent.parent
        for grade, grade_dir in GRADE_DIRS.items():
            for subject in ["az_dili", "riyaziyyat", "ingilis"]:
                filename = SUBJECT_MAP[subject]
                if isinstance(filename, dict):
                    filename = filename[grade_dir]
                pdf_path = base_dir / grade_dir / filename
                if pdf_path.exists():
                    toc = await process_textbook(str(pdf_path), subject, grade, gemini, qdrant)
                    await save_topics_to_db(toc, subject, grade)
                else:
                    print(f"SKIP: {pdf_path} not found")

    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: data pipeline with indexer and CLI runner for textbooks and DIM tests"
```

---

## Phase 4: Question Generation Engine

### Task 11: Generation Prompts

**Files:**
- Create: `testgen/backend/generation/__init__.py`
- Create: `testgen/backend/generation/prompts.py`
- Create: `testgen/backend/generation/schemas.py`

- [ ] **Step 1: Create generation schemas**

Create `testgen/backend/generation/__init__.py` (empty file).

Create `testgen/backend/generation/schemas.py`:

```python
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    subject: str
    grade: int
    topic: str
    difficulty: str  # easy, medium, hard
    question_type: str = "mcq"  # mcq, matching, open_ended


class GeneratedQuestion(BaseModel):
    question_text: str
    options: dict | None = None
    matching_pairs: dict | None = None
    correct_answer: str
    explanation: str
    bloom_level: str
    latex_content: str | None = None
    source_reference: str


class ValidationResult(BaseModel):
    answer_correct: bool
    textbook_aligned: bool
    original: bool
    bloom_accurate: bool
    grammar_quality: bool
    passed: bool
    feedback: str
```

- [ ] **Step 2: Create prompts module**

Create `testgen/backend/generation/prompts.py`:

```python
# Anderson & Krathwohl's revised Bloom taxonomy (2001)
BLOOM_MAP = {
    "easy": "Remember and Understand",
    "medium": "Apply and Analyze",
    "hard": "Evaluate and Create",
}

SYSTEM_PROMPT = """You are an expert test question creator for Azerbaijan's DIM (State Examination Center) university entrance exams.

You create high-quality, original test questions that:
1. Are grounded in official textbook content
2. Follow DIM exam format and style exactly
3. Target the specified Bloom's taxonomy cognitive level
4. Are written in proper Azerbaijani language
5. Have exactly one unambiguously correct answer (for MCQ)
6. Include a clear explanation referencing the textbook

CRITICAL: Generated questions must be ORIGINAL — not copies or close paraphrases of existing DIM questions."""


def build_generation_prompt(
    subject: str,
    grade: int,
    topic: str,
    difficulty: str,
    question_type: str,
    textbook_context: list[dict],
    dim_examples: list[dict],
) -> str:
    bloom = BLOOM_MAP[difficulty]

    context_text = "\n\n".join(
        f"[Textbook p.{c['payload'].get('pages', '?')}]: {c['payload']['text_content']}"
        for c in textbook_context
    )

    examples_text = "\n\n".join(
        f"[DIM Example]: {e['payload']['question_text']}\n"
        f"Options: {e['payload'].get('options', 'N/A')}\n"
        f"Answer: {e['payload'].get('correct_answer', 'N/A')}"
        for e in dim_examples
    )

    type_instructions = {
        "mcq": "Create a multiple-choice question with exactly 5 options (A-E). Exactly one option must be correct.",
        "matching": "Create a matching question with two columns. Provide matching_pairs as a dict mapping left items to right items.",
        "open_ended": "Create an open-ended question with a clear expected answer.",
    }

    return f"""TASK: Generate one ORIGINAL {question_type} question.

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}
DIFFICULTY: {difficulty}
BLOOM LEVEL: {bloom}

FORMAT: {type_instructions[question_type]}

TEXTBOOK CONTEXT (use this as the knowledge base):
{context_text}

DIM EXAMPLES (match this style, but create something NEW):
{examples_text}

IMPORTANT:
- The question must be answerable from the textbook context above
- Use Azerbaijani language
- For math, use LaTeX notation for formulas
- Do NOT copy or closely paraphrase any DIM example

Return JSON:
{{
  "question_text": "...",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."}} or null,
  "matching_pairs": {{...}} or null,
  "correct_answer": "A" or answer text,
  "explanation": "Explanation referencing the textbook content",
  "bloom_level": "{bloom}",
  "latex_content": "LaTeX if any math formulas" or null,
  "source_reference": "Textbook page reference"
}}"""


VALIDATION_PROMPT = """You are a quality assurance reviewer for DIM test questions.

Review this generated question against the textbook context and assess:

QUESTION:
{question_json}

TEXTBOOK CONTEXT:
{textbook_context}

TARGET BLOOM LEVEL: {bloom_level}

Evaluate each criterion (true/false):
1. answer_correct: Is the marked correct answer actually correct based on the textbook?
2. textbook_aligned: Is the question answerable from the given textbook content?
3. original: Is this question substantially different from common DIM questions (not a copy)?
4. bloom_accurate: Does the cognitive demand match the target Bloom level ({bloom_level})?
5. grammar_quality: Is the Azerbaijani language correct and natural?

Return JSON:
{{
  "answer_correct": true/false,
  "textbook_aligned": true/false,
  "original": true/false,
  "bloom_accurate": true/false,
  "grammar_quality": true/false,
  "passed": true/false (true only if ALL criteria are true),
  "feedback": "Brief explanation of any issues"
}}"""
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: generation schemas and prompt templates for question creation and validation"
```

---

### Task 12: Retrieval Stage

**Files:**
- Create: `testgen/backend/generation/retrieval.py`
- Test: `testgen/backend/tests/test_retrieval.py`

- [ ] **Step 1: Write failing test**

Create `testgen/backend/tests/test_retrieval.py`:

```python
import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_retrieval_returns_textbook_and_dim_context():
    from generation.retrieval import RetrievalStage

    mock_gemini = MagicMock()
    mock_gemini.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.side_effect = [
        [{"payload": {"text_content": "Textbook content"}, "score": 0.9}],
        [{"payload": {"question_text": "DIM question?"}, "score": 0.88}],
    ]

    stage = RetrievalStage(gemini=mock_gemini, qdrant=mock_qdrant)
    result = await stage.retrieve(
        subject="riyaziyyat",
        grade=9,
        topic="Tənliklər",
        question_type="mcq",
    )

    assert "textbook_context" in result
    assert "dim_examples" in result
    assert len(result["textbook_context"]) == 1
    assert len(result["dim_examples"]) == 1
    assert mock_qdrant.search.call_count == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_retrieval.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement retrieval stage**

Create `testgen/backend/generation/retrieval.py`:

```python
from core.gemini import GeminiClient
from core.qdrant import QdrantWrapper, TEXTBOOKS_COLLECTION, DIM_TESTS_COLLECTION


class RetrievalStage:
    def __init__(self, gemini: GeminiClient, qdrant: QdrantWrapper):
        self.gemini = gemini
        self.qdrant = qdrant

    async def retrieve(
        self,
        subject: str,
        grade: int,
        topic: str,
        question_type: str,
        textbook_limit: int = 5,
        dim_limit: int = 5,
    ) -> dict:
        query_text = f"{subject} {topic} grade {grade}"
        query_vector = await self.gemini.embed(query_text)

        textbook_context = self.qdrant.search(
            collection=TEXTBOOKS_COLLECTION,
            vector=query_vector,
            filters={"subject": subject, "grade": grade},
            limit=textbook_limit,
        )

        dim_examples = self.qdrant.search(
            collection=DIM_TESTS_COLLECTION,
            vector=query_vector,
            filters={"subject": subject},
            limit=dim_limit,
        )

        return {
            "textbook_context": textbook_context,
            "dim_examples": dim_examples,
        }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_retrieval.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: retrieval stage — dual Qdrant search for textbooks and DIM examples"
```

---

### Task 13: Generation & Validation Stages

**Files:**
- Create: `testgen/backend/generation/generator.py`
- Create: `testgen/backend/generation/validator.py`
- Test: `testgen/backend/tests/test_generation.py`

- [ ] **Step 1: Write failing tests**

Create `testgen/backend/tests/test_generation.py`:

```python
import json
import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_generator_produces_question():
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


@pytest.mark.asyncio
async def test_validator_passes_good_question():
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
    mock_gemini.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.6}]

    stage = ValidationStage(gemini=mock_gemini, qdrant=mock_qdrant, similarity_threshold=0.85)

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question,
        textbook_context=[{"payload": {"text_content": "Content"}}],
        bloom_level="Remember and Understand",
    )

    assert result["passed"] is True


@pytest.mark.asyncio
async def test_validator_rejects_too_similar():
    from generation.validator import ValidationStage

    mock_gemini = MagicMock()
    mock_gemini.embed = AsyncMock(return_value=[0.1] * 3072)

    mock_qdrant = MagicMock()
    mock_qdrant.search.return_value = [{"payload": {}, "score": 0.92}]  # above threshold

    stage = ValidationStage(gemini=mock_gemini, qdrant=mock_qdrant, similarity_threshold=0.85)

    question = {"question_text": "Test?", "correct_answer": "A"}
    result = await stage.validate(
        question=question,
        textbook_context=[],
        bloom_level="Remember and Understand",
    )

    assert result["passed"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_generation.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement generation stage**

Create `testgen/backend/generation/generator.py`:

```python
import json

from core.gemini import GeminiClient
from generation.prompts import SYSTEM_PROMPT, build_generation_prompt


class GenerationStage:
    def __init__(self, gemini: GeminiClient):
        self.gemini = gemini

    async def generate(
        self,
        subject: str,
        grade: int,
        topic: str,
        difficulty: str,
        question_type: str,
        textbook_context: list[dict],
        dim_examples: list[dict],
    ) -> dict:
        prompt = build_generation_prompt(
            subject=subject,
            grade=grade,
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            textbook_context=textbook_context,
            dim_examples=dim_examples,
        )

        response = await self.gemini.generate_json(prompt, system_instruction=SYSTEM_PROMPT)
        return json.loads(response)
```

- [ ] **Step 4: Implement validation stage**

Create `testgen/backend/generation/validator.py`:

```python
import json

from core.gemini import GeminiClient
from core.qdrant import QdrantWrapper, DIM_TESTS_COLLECTION
from generation.prompts import VALIDATION_PROMPT


class ValidationStage:
    def __init__(self, gemini: GeminiClient, qdrant: QdrantWrapper, similarity_threshold: float = 0.85):
        self.gemini = gemini
        self.qdrant = qdrant
        self.similarity_threshold = similarity_threshold

    async def validate(
        self,
        question: dict,
        textbook_context: list[dict],
        bloom_level: str,
    ) -> dict:
        # Stage 3A: Semantic similarity check
        question_vector = await self.gemini.embed(question["question_text"])
        similar = self.qdrant.search(
            collection=DIM_TESTS_COLLECTION,
            vector=question_vector,
            limit=1,
        )

        max_similarity = similar[0]["score"] if similar else 0.0

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

        # Stage 3B: LLM self-validation
        context_text = "\n".join(c["payload"].get("text_content", "") for c in textbook_context)

        prompt = VALIDATION_PROMPT.format(
            question_json=json.dumps(question, ensure_ascii=False),
            textbook_context=context_text,
            bloom_level=bloom_level,
        )

        response = await self.gemini.generate_json(prompt)
        result = json.loads(response)
        result["similarity_score"] = max_similarity
        return result
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_generation.py -v
```

Expected: All 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: generation and validation stages with similarity check and LLM review"
```

---

### Task 14: Pipeline Orchestrator & Generation API

**Files:**
- Create: `testgen/backend/generation/pipeline.py`
- Create: `testgen/backend/generation/router.py`
- Modify: `testgen/backend/main.py`
- Test: `testgen/backend/tests/test_generation.py` (append)

- [ ] **Step 1: Write failing test for pipeline orchestrator**

Append to `testgen/backend/tests/test_generation.py`:

```python
@pytest.mark.asyncio
async def test_pipeline_orchestrates_three_stages():
    from generation.pipeline import GenerationPipeline

    mock_retrieval = MagicMock()
    mock_retrieval.retrieve = AsyncMock(return_value={
        "textbook_context": [{"payload": {"text_content": "Content", "pages": "5"}}],
        "dim_examples": [{"payload": {"question_text": "Q?", "options": {}, "correct_answer": "A"}}],
    })

    mock_generator = MagicMock()
    mock_generator.generate = AsyncMock(return_value={
        "question_text": "New question?",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"},
        "correct_answer": "A",
        "explanation": "Because...",
        "bloom_level": "Remember",
        "latex_content": None,
        "source_reference": "p.5",
    })

    mock_validator = MagicMock()
    mock_validator.validate = AsyncMock(return_value={
        "passed": True,
        "answer_correct": True,
        "textbook_aligned": True,
        "original": True,
        "bloom_accurate": True,
        "grammar_quality": True,
        "feedback": "Good",
        "similarity_score": 0.3,
    })

    pipeline = GenerationPipeline(
        retrieval=mock_retrieval,
        generator=mock_generator,
        validator=mock_validator,
        max_attempts=3,
    )

    result = await pipeline.run(
        subject="riyaziyyat",
        grade=9,
        topic="Tənliklər",
        difficulty="easy",
        question_type="mcq",
    )

    assert result["question"]["question_text"] == "New question?"
    assert result["validation"]["passed"] is True
    assert result["attempts"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_generation.py::test_pipeline_orchestrates_three_stages -v
```

Expected: FAIL.

- [ ] **Step 3: Implement pipeline orchestrator**

Create `testgen/backend/generation/pipeline.py`:

```python
import time

from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.prompts import BLOOM_MAP


class GenerationPipeline:
    def __init__(
        self,
        retrieval: RetrievalStage,
        generator: GenerationStage,
        validator: ValidationStage,
        max_attempts: int = 3,
    ):
        self.retrieval = retrieval
        self.generator = generator
        self.validator = validator
        self.max_attempts = max_attempts

    async def run(
        self,
        subject: str,
        grade: int,
        topic: str,
        difficulty: str,
        question_type: str = "mcq",
    ) -> dict:
        total_start = time.time()

        # Stage 1: Retrieval
        retrieval_start = time.time()
        context = await self.retrieval.retrieve(
            subject=subject,
            grade=grade,
            topic=topic,
            question_type=question_type,
        )
        retrieval_time = time.time() - retrieval_start

        bloom_level = BLOOM_MAP[difficulty]

        for attempt in range(1, self.max_attempts + 1):
            # Stage 2: Generation
            gen_start = time.time()
            question = await self.generator.generate(
                subject=subject,
                grade=grade,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                textbook_context=context["textbook_context"],
                dim_examples=context["dim_examples"],
            )
            generation_time = time.time() - gen_start

            # Stage 3: Validation
            val_start = time.time()
            validation = await self.validator.validate(
                question=question,
                textbook_context=context["textbook_context"],
                bloom_level=bloom_level,
            )
            validation_time = time.time() - val_start

            if validation["passed"]:
                return {
                    "question": question,
                    "validation": validation,
                    "attempts": attempt,
                    "timing": {
                        "retrieval": retrieval_time,
                        "generation": generation_time,
                        "validation": validation_time,
                        "total": time.time() - total_start,
                    },
                }

        # All attempts failed — return last result with failure
        return {
            "question": question,
            "validation": validation,
            "attempts": self.max_attempts,
            "timing": {
                "retrieval": retrieval_time,
                "generation": generation_time,
                "validation": validation_time,
                "total": time.time() - total_start,
            },
        }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_generation.py::test_pipeline_orchestrates_three_stages -v
```

Expected: PASS.

- [ ] **Step 5: Create generation API router**

Create `testgen/backend/generation/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.database import get_db
from core.gemini import GeminiClient
from core.qdrant import QdrantWrapper
from auth.security import get_current_user
from models.user import User
from models.question import Question
from models.generation_log import GenerationLog
from generation.schemas import GenerateRequest
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.pipeline import GenerationPipeline

router = APIRouter(prefix="/api/generation", tags=["generation"])


def get_pipeline() -> GenerationPipeline:
    gemini = GeminiClient(api_key=settings.gemini_api_key)
    qdrant = QdrantWrapper(url=settings.qdrant_url)
    return GenerationPipeline(
        retrieval=RetrievalStage(gemini=gemini, qdrant=qdrant),
        generator=GenerationStage(gemini=gemini),
        validator=ValidationStage(gemini=gemini, qdrant=qdrant, similarity_threshold=settings.similarity_threshold),
        max_attempts=settings.max_generation_attempts,
    )


@router.post("/generate")
async def generate_question(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pipeline = get_pipeline()
    result = await pipeline.run(
        subject=req.subject,
        grade=req.grade,
        topic=req.topic,
        difficulty=req.difficulty,
        question_type=req.question_type,
    )

    if not result["validation"]["passed"]:
        # Log the failed attempt
        log = GenerationLog(
            user_id=user.id,
            subject=req.subject,
            topic=req.topic,
            difficulty=req.difficulty,
            retrieval_time=result["timing"]["retrieval"],
            generation_time=result["timing"]["generation"],
            validation_time=result["timing"]["validation"],
            total_time=result["timing"]["total"],
            attempts=result["attempts"],
            success=False,
        )
        db.add(log)
        await db.commit()
        raise HTTPException(status_code=422, detail="Failed to generate valid question after max attempts")

    # Save question to DB
    q = result["question"]
    question = Question(
        subject=req.subject,
        grade=req.grade,
        topic=req.topic,
        question_type=req.question_type,
        difficulty=req.difficulty,
        bloom_level=q["bloom_level"],
        question_text=q["question_text"],
        options=q.get("options"),
        matching_pairs=q.get("matching_pairs"),
        correct_answer=q["correct_answer"],
        explanation=q["explanation"],
        latex_content=q.get("latex_content"),
        source_reference=q["source_reference"],
        similarity_score=result["validation"].get("similarity_score", 0.0),
        validation_result=result["validation"],
        created_by=user.id,
    )
    db.add(question)
    await db.flush()

    # Log success
    log = GenerationLog(
        user_id=user.id,
        question_id=question.id,
        subject=req.subject,
        topic=req.topic,
        difficulty=req.difficulty,
        retrieval_time=result["timing"]["retrieval"],
        generation_time=result["timing"]["generation"],
        validation_time=result["timing"]["validation"],
        total_time=result["timing"]["total"],
        attempts=result["attempts"],
        success=True,
    )
    db.add(log)
    await db.commit()

    return {
        "question": q,
        "question_id": str(question.id),
        "attempts": result["attempts"],
        "timing": result["timing"],
    }
```

Add router to `testgen/backend/main.py`:

```python
from generation.router import router as generation_router

app.include_router(generation_router)
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: 3-stage generation pipeline orchestrator and /api/generation/generate endpoint"
```

---

## Phase 5: REST API Layer

### Task 15: Question Bank CRUD

**Files:**
- Create: `testgen/backend/questions/__init__.py`
- Create: `testgen/backend/questions/schemas.py`
- Create: `testgen/backend/questions/service.py`
- Create: `testgen/backend/questions/router.py`
- Modify: `testgen/backend/main.py`
- Test: `testgen/backend/tests/test_questions.py`

- [ ] **Step 1: Write failing tests**

Create `testgen/backend/tests/test_questions.py`:

```python
import pytest


async def create_user_and_login(client):
    await client.post("/api/auth/register", json={
        "email": "teacher@test.com",
        "password": "pass123",
        "full_name": "Teacher",
        "role": "teacher",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "teacher@test.com",
        "password": "pass123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_questions_empty(client):
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
    token = await create_user_and_login(client)
    response = await client.get(
        "/api/questions/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_questions.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement question schemas, service, and router**

Create `testgen/backend/questions/__init__.py` (empty file).

Create `testgen/backend/questions/schemas.py`:

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: uuid.UUID
    subject: str
    grade: int
    topic: str
    subtopic: str | None
    question_type: str
    difficulty: str
    bloom_level: str
    question_text: str
    options: dict | None
    matching_pairs: dict | None
    correct_answer: str
    explanation: str
    latex_content: str | None
    source_reference: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    options: dict | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    status: str | None = None


class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int
```

Create `testgen/backend/questions/service.py`:

```python
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.question import Question


async def list_questions(
    db: AsyncSession,
    subject: str | None = None,
    grade: int | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    status: str = "active",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Question], int]:
    query = select(Question)
    count_query = select(func.count(Question.id))

    if subject:
        query = query.where(Question.subject == subject)
        count_query = count_query.where(Question.subject == subject)
    if grade:
        query = query.where(Question.grade == grade)
        count_query = count_query.where(Question.grade == grade)
    if topic:
        query = query.where(Question.topic == topic)
        count_query = count_query.where(Question.topic == topic)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
        count_query = count_query.where(Question.difficulty == difficulty)
    if status:
        query = query.where(Question.status == status)
        count_query = count_query.where(Question.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Question.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all(), total


async def get_question(db: AsyncSession, question_id: uuid.UUID) -> Question | None:
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def update_question(db: AsyncSession, question_id: uuid.UUID, updates: dict) -> Question | None:
    question = await get_question(db, question_id)
    if not question:
        return None
    for key, value in updates.items():
        if value is not None:
            setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question_id: uuid.UUID) -> bool:
    question = await get_question(db, question_id)
    if not question:
        return False
    await db.delete(question)
    await db.commit()
    return True
```

Create `testgen/backend/questions/router.py`:

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from models.user import User
from questions.schemas import QuestionResponse, QuestionUpdate, QuestionListResponse
from questions.service import list_questions, get_question, update_question, delete_question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=QuestionListResponse)
async def list_all(
    subject: str | None = None,
    grade: int | None = None,
    topic: str | None = None,
    difficulty: str | None = None,
    status: str = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = await list_questions(db, subject, grade, topic, difficulty, status, page, page_size)
    return QuestionListResponse(
        items=[QuestionResponse.model_validate(q) for q in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_one(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    question = await get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionResponse.model_validate(question)


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update(
    question_id: uuid.UUID,
    body: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    question = await update_question(db, question_id, body.model_dump(exclude_unset=True))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QuestionResponse.model_validate(question)


@router.delete("/{question_id}", status_code=204)
async def delete(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    if not await delete_question(db, question_id):
        raise HTTPException(status_code=404, detail="Question not found")
```

Add to `testgen/backend/main.py`:

```python
from questions.router import router as questions_router

app.include_router(questions_router)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_questions.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: question bank CRUD API with filtering and pagination"
```

---

### Task 16: Subjects & Topics API

**Files:**
- Create: `testgen/backend/subjects/__init__.py`
- Create: `testgen/backend/subjects/router.py`
- Create: `testgen/backend/subjects/schemas.py`
- Modify: `testgen/backend/main.py`

- [ ] **Step 1: Implement subjects router**

Create `testgen/backend/subjects/__init__.py` (empty file).

Create `testgen/backend/subjects/schemas.py`:

```python
from pydantic import BaseModel


class SubjectInfo(BaseModel):
    id: str
    name: str
    name_az: str


class TopicInfo(BaseModel):
    chapter: str
    chapter_order: int
    topic: str
    subtopic: str | None
    page_start: int | None
    page_end: int | None

    model_config = {"from_attributes": True}
```

Create `testgen/backend/subjects/router.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.topic import Topic
from subjects.schemas import SubjectInfo, TopicInfo

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

SUBJECTS = [
    SubjectInfo(id="az_dili", name="Azerbaijani Language", name_az="Azərbaycan dili"),
    SubjectInfo(id="riyaziyyat", name="Mathematics", name_az="Riyaziyyat"),
    SubjectInfo(id="ingilis", name="English Language", name_az="İngilis dili"),
]


@router.get("", response_model=list[SubjectInfo])
async def list_subjects():
    return SUBJECTS


@router.get("/{subject_id}/topics", response_model=list[TopicInfo])
async def get_topics(
    subject_id: str,
    grade: int = Query(..., ge=9, le=11),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Topic)
        .where(Topic.subject == subject_id, Topic.grade == grade)
        .order_by(Topic.chapter_order, Topic.topic)
    )
    topics = result.scalars().all()
    return [TopicInfo.model_validate(t) for t in topics]
```

Add to `testgen/backend/main.py`:

```python
from subjects.router import router as subjects_router

app.include_router(subjects_router)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: subjects and topics API from cached topic tree"
```

---

### Task 17: Variant Generation & Export

**Files:**
- Create: `testgen/backend/variants/__init__.py`
- Create: `testgen/backend/variants/schemas.py`
- Create: `testgen/backend/variants/service.py`
- Create: `testgen/backend/variants/export.py`
- Create: `testgen/backend/variants/router.py`
- Modify: `testgen/backend/main.py`
- Test: `testgen/backend/tests/test_variants.py`

- [ ] **Step 1: Write failing test**

Create `testgen/backend/tests/test_variants.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_variants.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement variant schemas, service, export, and router**

Create `testgen/backend/variants/__init__.py` (empty file).

Create `testgen/backend/variants/schemas.py`:

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class VariantCreateRequest(BaseModel):
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict  # {"easy": 10, "medium": 10, "hard": 5}
    topic_dist: dict | None = None  # {"topic1": 5, "topic2": 10} or null for auto
    grade: int = 9


class VariantResponse(BaseModel):
    id: uuid.UUID
    title: str
    subject: str
    total_questions: int
    difficulty_dist: dict
    created_at: datetime

    model_config = {"from_attributes": True}
```

Create `testgen/backend/variants/service.py`:

```python
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.variant import Variant, VariantQuestion
from models.question import Question
from generation.pipeline import GenerationPipeline


async def create_variant(
    db: AsyncSession,
    pipeline: GenerationPipeline,
    user_id: uuid.UUID,
    title: str,
    subject: str,
    grade: int,
    total_questions: int,
    difficulty_dist: dict,
    topic_dist: dict | None = None,
) -> Variant:
    variant = Variant(
        title=title,
        subject=subject,
        total_questions=total_questions,
        difficulty_dist=difficulty_dist,
        created_by=user_id,
    )
    db.add(variant)
    await db.flush()

    # Build task list from difficulty + topic distributions
    tasks = []
    topics = list(topic_dist.keys()) if topic_dist else [subject]
    for difficulty, count in difficulty_dist.items():
        for i in range(count):
            # Round-robin across topics to distribute evenly
            topic = topics[i % len(topics)]
            tasks.append((topic, difficulty))

    # Generate questions (5 concurrent)
    semaphore = asyncio.Semaphore(5)
    order = 0
    question_ids = []

    async def gen_one(topic: str, difficulty: str):
        async with semaphore:
            return await pipeline.run(
                subject=subject,
                grade=grade,
                topic=topic,
                difficulty=difficulty,
            )

    results = await asyncio.gather(
        *[gen_one(t, d) for t, d in tasks],
        return_exceptions=True,
    )

    for i, result in enumerate(results):
        if isinstance(result, Exception) or not result["validation"]["passed"]:
            continue

        q = result["question"]
        question = Question(
            subject=subject,
            grade=grade,
            topic=tasks[i][0],
            question_type="mcq",
            difficulty=tasks[i][1],
            bloom_level=q["bloom_level"],
            question_text=q["question_text"],
            options=q.get("options"),
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            latex_content=q.get("latex_content"),
            source_reference=q["source_reference"],
            similarity_score=result["validation"].get("similarity_score", 0.0),
            validation_result=result["validation"],
            created_by=user_id,
        )
        db.add(question)
        await db.flush()

        vq = VariantQuestion(variant_id=variant.id, question_id=question.id, order_number=i + 1)
        db.add(vq)

    await db.commit()
    await db.refresh(variant)
    return variant


async def list_variants(db: AsyncSession, user_id: uuid.UUID) -> list[Variant]:
    result = await db.execute(
        select(Variant).where(Variant.created_by == user_id).order_by(Variant.created_at.desc())
    )
    return result.scalars().all()


async def get_variant_with_questions(db: AsyncSession, variant_id: uuid.UUID) -> dict | None:
    result = await db.execute(select(Variant).where(Variant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        return None

    vq_result = await db.execute(
        select(VariantQuestion, Question)
        .join(Question, VariantQuestion.question_id == Question.id)
        .where(VariantQuestion.variant_id == variant_id)
        .order_by(VariantQuestion.order_number)
    )
    questions = [{"order": vq.order_number, "question": q} for vq, q in vq_result.all()]

    return {"variant": variant, "questions": questions}
```

Create `testgen/backend/variants/export.py`:

```python
import json
from io import BytesIO


def export_json(variant_data: dict) -> bytes:
    questions = []
    for item in variant_data["questions"]:
        q = item["question"]
        questions.append({
            "order": item["order"],
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "topic": q.topic,
        })

    result = {
        "title": variant_data["variant"].title,
        "subject": variant_data["variant"].subject,
        "total_questions": variant_data["variant"].total_questions,
        "questions": questions,
    }
    return json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")


def export_text(variant_data: dict) -> str:
    """Simple text export. PDF/Word export can be added with reportlab/python-docx."""
    lines = [
        f"# {variant_data['variant'].title}",
        f"Fənn: {variant_data['variant'].subject}",
        f"Sual sayı: {variant_data['variant'].total_questions}",
        "",
    ]
    for item in variant_data["questions"]:
        q = item["question"]
        lines.append(f"**{item['order']}.** {q.question_text}")
        if q.options:
            for key, val in q.options.items():
                lines.append(f"   {key}) {val}")
        lines.append("")

    lines.append("\n--- Cavablar ---\n")
    for item in variant_data["questions"]:
        q = item["question"]
        lines.append(f"{item['order']}. {q.correct_answer}")

    return "\n".join(lines)
```

Create `testgen/backend/variants/router.py`:

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.database import get_db
from core.gemini import GeminiClient
from core.qdrant import QdrantWrapper
from auth.security import get_current_user
from models.user import User
from generation.retrieval import RetrievalStage
from generation.generator import GenerationStage
from generation.validator import ValidationStage
from generation.pipeline import GenerationPipeline
from variants.schemas import VariantCreateRequest, VariantResponse
from variants.service import create_variant, list_variants, get_variant_with_questions
from variants.export import export_json, export_text

router = APIRouter(prefix="/api/variants", tags=["variants"])


def get_pipeline() -> GenerationPipeline:
    gemini = GeminiClient(api_key=settings.gemini_api_key)
    qdrant = QdrantWrapper(url=settings.qdrant_url)
    return GenerationPipeline(
        retrieval=RetrievalStage(gemini=gemini, qdrant=qdrant),
        generator=GenerationStage(gemini=gemini),
        validator=ValidationStage(gemini=gemini, qdrant=qdrant, similarity_threshold=settings.similarity_threshold),
        max_attempts=settings.max_generation_attempts,
    )


@router.post("/generate", response_model=VariantResponse, status_code=201)
async def generate_variant(
    req: VariantCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")

    pipeline = get_pipeline()
    variant = await create_variant(
        db=db,
        pipeline=pipeline,
        user_id=user.id,
        title=req.title,
        subject=req.subject,
        grade=req.grade,
        total_questions=req.total_questions,
        difficulty_dist=req.difficulty_dist,
        topic_dist=req.topic_dist,
    )
    return VariantResponse.model_validate(variant)


@router.get("", response_model=list[VariantResponse])
async def list_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    variants = await list_variants(db, user.id)
    return [VariantResponse.model_validate(v) for v in variants]


@router.get("/{variant_id}")
async def get_one(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await get_variant_with_questions(db, variant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Variant not found")
    return data


@router.get("/{variant_id}/export")
async def export(
    variant_id: uuid.UUID,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await get_variant_with_questions(db, variant_id)
    if not data:
        raise HTTPException(status_code=404, detail="Variant not found")

    if format == "json":
        content = export_json(data)
        return Response(content=content, media_type="application/json",
                        headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.json"})
    else:
        content = export_text(data)
        return Response(content=content.encode("utf-8"), media_type="text/plain",
                        headers={"Content-Disposition": f"attachment; filename=variant_{variant_id}.txt"})
```

Add to `testgen/backend/main.py`:

```python
from variants.router import router as variants_router

app.include_router(variants_router)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_variants.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: variant generation with concurrent pipeline execution and export"
```

---

### Task 18: Reports API

**Files:**
- Create: `testgen/backend/reports/__init__.py`
- Create: `testgen/backend/reports/schemas.py`
- Create: `testgen/backend/reports/service.py`
- Create: `testgen/backend/reports/router.py`
- Modify: `testgen/backend/main.py`

- [ ] **Step 1: Implement reports module**

Create `testgen/backend/reports/__init__.py` (empty file).

Create `testgen/backend/reports/schemas.py`:

```python
import uuid
from datetime import datetime
from pydantic import BaseModel


class ReportCreateRequest(BaseModel):
    question_id: uuid.UUID
    report_type: str  # wrong_answer, unclear, off_topic, duplicate, grammar, other
    comment: str | None = None


class ReportResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    reported_by: uuid.UUID
    report_type: str
    comment: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportResolveRequest(BaseModel):
    status: str  # fixed, rejected
```

Create `testgen/backend/reports/service.py`:

```python
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.report import Report
from models.question import Question


async def create_report(
    db: AsyncSession,
    question_id: uuid.UUID,
    user_id: uuid.UUID,
    report_type: str,
    comment: str | None,
) -> Report:
    report = Report(
        question_id=question_id,
        reported_by=user_id,
        report_type=report_type,
        comment=comment,
    )
    db.add(report)

    # Increment report count on question
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if question:
        question.report_count += 1
        if question.report_count >= 3:
            question.status = "reported"

    await db.commit()
    await db.refresh(report)
    return report


async def list_reports(db: AsyncSession, status: str | None = None) -> list[Report]:
    query = select(Report).order_by(Report.created_at.desc())
    if status:
        query = query.where(Report.status == status)
    result = await db.execute(query)
    return result.scalars().all()


async def resolve_report(db: AsyncSession, report_id: uuid.UUID, new_status: str) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        return None
    report.status = new_status
    await db.commit()
    await db.refresh(report)
    return report
```

Create `testgen/backend/reports/router.py`:

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from models.user import User
from reports.schemas import ReportCreateRequest, ReportResponse, ReportResolveRequest
from reports.service import create_report, list_reports, resolve_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=201)
async def report_question(
    req: ReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = await create_report(db, req.question_id, user.id, req.report_type, req.comment)
    return ReportResponse.model_validate(report)


@router.get("", response_model=list[ReportResponse])
async def list_all(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    reports = await list_reports(db, status)
    return [ReportResponse.model_validate(r) for r in reports]


@router.patch("/{report_id}", response_model=ReportResponse)
async def resolve(
    report_id: uuid.UUID,
    req: ReportResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    report = await resolve_report(db, report_id, req.status)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)
```

Add to `testgen/backend/main.py`:

```python
from reports.router import router as reports_router

app.include_router(reports_router)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: reports API for error reporting and teacher resolution"
```

---

### Task 18B: Stats API Endpoint

**Files:**
- Modify: `testgen/backend/main.py`

- [ ] **Step 1: Add stats endpoint directly to main**

Append to `testgen/backend/main.py`:

```python
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from auth.security import get_current_user
from models.user import User
from models.question import Question
from models.generation_log import GenerationLog


@app.get("/api/stats/dashboard")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_questions = (await db.execute(select(func.count(Question.id)))).scalar() or 0
    total_generations = (await db.execute(select(func.count(GenerationLog.id)))).scalar() or 0
    success_count = (await db.execute(
        select(func.count(GenerationLog.id)).where(GenerationLog.success == True)
    )).scalar() or 0
    avg_time = (await db.execute(select(func.avg(GenerationLog.total_time)))).scalar() or 0

    return {
        "total_questions": total_questions,
        "total_generations": total_generations,
        "success_rate": (success_count / total_generations * 100) if total_generations > 0 else 0,
        "avg_generation_time": round(avg_time, 2),
    }
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: dashboard stats endpoint"
```

---

## Phase 6: Frontend

### Task 19: Next.js Setup & Auth Pages

**Files:**
- Create: `testgen/frontend/next.config.js`
- ~~Create: `testgen/frontend/tailwind.config.js`~~ (not needed in Tailwind CSS 4)
- Create: `testgen/frontend/postcss.config.js`
- Create: `testgen/frontend/tsconfig.json`
- Create: `testgen/frontend/src/styles/globals.css`
- Create: `testgen/frontend/src/lib/types.ts`
- Create: `testgen/frontend/src/lib/api.ts`
- Create: `testgen/frontend/src/lib/auth.ts`
- Create: `testgen/frontend/src/app/layout.tsx`
- Create: `testgen/frontend/src/app/page.tsx`
- Create: `testgen/frontend/src/app/login/page.tsx`
- Create: `testgen/frontend/src/app/register/page.tsx`
- Create: `testgen/frontend/src/components/Navbar.tsx`

- [ ] **Step 1: Create Next.js config files**

Create `testgen/frontend/next.config.js`:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}
module.exports = nextConfig
```

Create `testgen/frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Create `testgen/frontend/postcss.config.js`:

```js
module.exports = {
  plugins: { '@tailwindcss/postcss': {} },
}
```

> **Note:** Tailwind CSS 4 uses CSS-first configuration — no `tailwind.config.js` needed. Content detection is automatic.

Create `testgen/frontend/src/styles/globals.css`:

```css
@import "tailwindcss";
```

- [ ] **Step 2: Create shared types and API client**

Create `testgen/frontend/src/lib/types.ts`:

```ts
export interface User {
  id: string
  email: string
  full_name: string
  role: 'student' | 'teacher'
  created_at: string
}

export interface Question {
  id: string
  subject: string
  grade: number
  topic: string
  subtopic: string | null
  question_type: 'mcq' | 'matching' | 'open_ended'
  difficulty: 'easy' | 'medium' | 'hard'
  bloom_level: string
  question_text: string
  options: Record<string, string> | null
  matching_pairs: Record<string, string> | null
  correct_answer: string
  explanation: string
  latex_content: string | null
  source_reference: string
  status: string
  created_at: string
}

export interface GenerateRequest {
  subject: string
  grade: number
  topic: string
  difficulty: string
  question_type: string
}

export interface GenerateResponse {
  question: Question
  question_id: string
  attempts: number
  timing: { retrieval: number; generation: number; validation: number; total: number }
}

export interface TopicInfo {
  chapter: string
  chapter_order: number
  topic: string
  subtopic: string | null
}

export interface SubjectInfo {
  id: string
  name: string
  name_az: string
}
```

Create `testgen/frontend/src/lib/api.ts`:

```ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || 'Request failed')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; full_name: string; role: string }) =>
      request('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
      request<{ access_token: string }>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    me: () => request<import('./types').User>('/api/auth/me'),
  },
  subjects: {
    list: () => request<import('./types').SubjectInfo[]>('/api/subjects'),
    topics: (subjectId: string, grade: number) =>
      request<import('./types').TopicInfo[]>(`/api/subjects/${subjectId}/topics?grade=${grade}`),
  },
  questions: {
    generate: (data: import('./types').GenerateRequest) =>
      request<import('./types').GenerateResponse>('/api/generation/generate', { method: 'POST', body: JSON.stringify(data) }),
    list: (params: string) => request<{ items: import('./types').Question[]; total: number }>(`/api/questions?${params}`),
  },
  variants: {
    generate: (data: any) => request('/api/variants/generate', { method: 'POST', body: JSON.stringify(data) }),
    list: () => request<any[]>('/api/variants'),
    get: (id: string) => request<any>(`/api/variants/${id}`),
    export: (id: string, format: string) => `${API_URL}/api/variants/${id}/export?format=${format}`,
  },
  reports: {
    create: (data: { question_id: string; report_type: string; comment?: string }) =>
      request('/api/reports', { method: 'POST', body: JSON.stringify(data) }),
    list: (status?: string) => request<any[]>(`/api/reports${status ? `?status=${status}` : ''}`),
    resolve: (id: string, status: string) =>
      request(`/api/reports/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  },
  stats: {
    dashboard: () => request<any>('/api/stats/dashboard'),
  },
}
```

Create `testgen/frontend/src/lib/auth.ts`:

```ts
'use client'
import { useEffect, useState } from 'react'
import { api } from './api'
import type { User } from './types'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }
    api.auth.me()
      .then(setUser)
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    const { access_token } = await api.auth.login({ email, password })
    localStorage.setItem('token', access_token)
    const me = await api.auth.me()
    setUser(me)
    return me
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return { user, loading, login, logout }
}
```

- [ ] **Step 3: Create layout and navbar**

Create `testgen/frontend/src/components/Navbar.tsx`:

```tsx
'use client'
import Link from 'next/link'
import { useAuth } from '@/lib/auth'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white border-b px-6 py-3 flex items-center justify-between">
      <Link href="/" className="text-xl font-bold text-blue-600">TestGen AI</Link>
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <span className="text-sm text-gray-600">{user.full_name}</span>
            {user.role === 'teacher' ? (
              <Link href="/teacher/dashboard" className="text-sm text-blue-600 hover:underline">Panel</Link>
            ) : (
              <Link href="/generate" className="text-sm text-blue-600 hover:underline">Sual yarat</Link>
            )}
            <button onClick={logout} className="text-sm text-red-500 hover:underline">Çıxış</button>
          </>
        ) : (
          <>
            <Link href="/login" className="text-sm text-blue-600 hover:underline">Daxil ol</Link>
            <Link href="/register" className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Qeydiyyat</Link>
          </>
        )}
      </div>
    </nav>
  )
}
```

Create `testgen/frontend/src/app/layout.tsx`:

```tsx
import type { Metadata } from 'next'
import Navbar from '@/components/Navbar'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'TestGen AI',
  description: 'AI-powered test question generation for DIM exams',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="az">
      <body className="bg-gray-50 min-h-screen">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  )
}
```

Create `testgen/frontend/src/app/page.tsx`:

```tsx
import Link from 'next/link'

export default function Home() {
  return (
    <div className="text-center py-20">
      <h1 className="text-4xl font-bold mb-4">TestGen AI</h1>
      <p className="text-xl text-gray-600 mb-8">
        DIM imtahan suallarinin suni intellekt ile avtomatik generasiyasi
      </p>
      <div className="flex gap-4 justify-center">
        <Link href="/register" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Baslayaq
        </Link>
        <Link href="/login" className="px-6 py-3 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50">
          Daxil ol
        </Link>
      </div>
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        <div className="p-6 bg-white rounded-lg shadow">
          <h3 className="font-bold mb-2">Azərbaycan dili</h3>
          <p className="text-gray-600 text-sm">9-11-ci sinif dersliklerine uygun test suallari</p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow">
          <h3 className="font-bold mb-2">Riyaziyyat</h3>
          <p className="text-gray-600 text-sm">Formullar, tenllikler ve mentiqi suallar</p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow">
          <h3 className="font-bold mb-2">Ingilis dili</h3>
          <p className="text-gray-600 text-sm">Grammar, vocabulary ve reading comprehension</p>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create login and register pages**

Create `testgen/frontend/src/app/login/page.tsx`:

```tsx
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      router.push(user.role === 'teacher' ? '/teacher/dashboard' : '/generate')
    } catch (err: any) {
      setError(err.message || 'Daxil olmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-6">Daxil ol</h1>
      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded" required />
        <input type="password" placeholder="Şifrə" value={password} onChange={e => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded" required />
        <button type="submit" disabled={loading}
          className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Yüklənir...' : 'Daxil ol'}
        </button>
      </form>
      <p className="mt-4 text-sm text-center">
        Hesabınız yoxdur? <Link href="/register" className="text-blue-600 hover:underline">Qeydiyyat</Link>
      </p>
    </div>
  )
}
```

Create `testgen/frontend/src/app/register/page.tsx`:

```tsx
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '', role: 'student' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.auth.register(form)
      router.push('/login')
    } catch (err: any) {
      setError(err.message || 'Qeydiyyat mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-6">Qeydiyyat</h1>
      {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="text" placeholder="Ad Soyad" value={form.full_name}
          onChange={e => setForm({ ...form, full_name: e.target.value })}
          className="w-full px-4 py-2 border rounded" required />
        <input type="email" placeholder="Email" value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
          className="w-full px-4 py-2 border rounded" required />
        <input type="password" placeholder="Şifrə" value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
          className="w-full px-4 py-2 border rounded" required />
        <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}
          className="w-full px-4 py-2 border rounded">
          <option value="student">Tələbə (Abituriyent)</option>
          <option value="teacher">Müəllim</option>
        </select>
        <button type="submit" disabled={loading}
          className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Yüklənir...' : 'Qeydiyyatdan keç'}
        </button>
      </form>
      <p className="mt-4 text-sm text-center">
        Artıq hesabınız var? <Link href="/login" className="text-blue-600 hover:underline">Daxil ol</Link>
      </p>
    </div>
  )
}
```

- [ ] **Step 5: Install dependencies and verify build**

```bash
cd testgen/frontend
npm install
npm run build
```

Expected: Build succeeds.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: Next.js frontend setup with auth pages, API client, and landing page"
```

---

### Task 20: Student Question Generation UI

**Files:**
- Create: `testgen/frontend/src/components/GenerateForm.tsx`
- Create: `testgen/frontend/src/components/TopicSelector.tsx`
- Create: `testgen/frontend/src/components/DifficultyPicker.tsx`
- Create: `testgen/frontend/src/components/QuestionCard.tsx`
- Create: `testgen/frontend/src/components/LatexRenderer.tsx`
- Create: `testgen/frontend/src/components/ReportButton.tsx`
- Create: `testgen/frontend/src/app/generate/page.tsx`

- [ ] **Step 1: Create reusable components**

Create `testgen/frontend/src/components/LatexRenderer.tsx`:

```tsx
'use client'
import { useEffect, useRef } from 'react'
import katex from 'katex'

export default function LatexRenderer({ content }: { content: string }) {
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (!ref.current || !content) return
    // Replace LaTeX delimiters and render
    const parts = content.split(/(\$[^$]+\$)/g)
    ref.current.innerHTML = parts.map(part => {
      if (part.startsWith('$') && part.endsWith('$')) {
        try {
          return katex.renderToString(part.slice(1, -1), { throwOnError: false })
        } catch { return part }
      }
      return part
    }).join('')
  }, [content])

  return <span ref={ref}>{content}</span>
}
```

Create `testgen/frontend/src/components/TopicSelector.tsx`:

```tsx
'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { TopicInfo } from '@/lib/types'

interface Props {
  subject: string
  grade: number
  value: string
  onChange: (topic: string) => void
}

export default function TopicSelector({ subject, grade, value, onChange }: Props) {
  const [topics, setTopics] = useState<TopicInfo[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!subject || !grade) return
    setLoading(true)
    api.subjects.topics(subject, grade)
      .then(setTopics)
      .catch(() => setTopics([]))
      .finally(() => setLoading(false))
  }, [subject, grade])

  if (loading) return <select disabled className="w-full px-4 py-2 border rounded"><option>Yüklənir...</option></select>

  return (
    <select value={value} onChange={e => onChange(e.target.value)} className="w-full px-4 py-2 border rounded">
      <option value="">Mövzu seçin</option>
      {topics.map((t, i) => (
        <option key={i} value={t.topic}>{t.chapter} - {t.topic}</option>
      ))}
    </select>
  )
}
```

Create `testgen/frontend/src/components/DifficultyPicker.tsx`:

```tsx
interface Props {
  value: string
  onChange: (difficulty: string) => void
}

const levels = [
  { id: 'easy', label: 'Asan', color: 'bg-green-100 border-green-400 text-green-700' },
  { id: 'medium', label: 'Orta', color: 'bg-yellow-100 border-yellow-400 text-yellow-700' },
  { id: 'hard', label: 'Cetin', color: 'bg-red-100 border-red-400 text-red-700' },
]

export default function DifficultyPicker({ value, onChange }: Props) {
  return (
    <div className="flex gap-2">
      {levels.map(level => (
        <button
          key={level.id}
          type="button"
          onClick={() => onChange(level.id)}
          className={`px-4 py-2 border rounded transition ${
            value === level.id ? level.color + ' border-2' : 'bg-gray-50 text-gray-500'
          }`}
        >
          {level.label}
        </button>
      ))}
    </div>
  )
}
```

Create `testgen/frontend/src/components/ReportButton.tsx`:

```tsx
'use client'
import { useState } from 'react'
import { api } from '@/lib/api'

interface Props {
  questionId: string
}

export default function ReportButton({ questionId }: Props) {
  const [open, setOpen] = useState(false)
  const [type, setType] = useState('wrong_answer')
  const [comment, setComment] = useState('')
  const [sent, setSent] = useState(false)

  const submit = async () => {
    await api.reports.create({ question_id: questionId, report_type: type, comment: comment || undefined })
    setSent(true)
    setOpen(false)
  }

  if (sent) return <span className="text-sm text-green-600">Gonderildi</span>

  return (
    <>
      <button onClick={() => setOpen(!open)} className="text-sm text-red-500 hover:underline">Xeta bildir</button>
      {open && (
        <div className="mt-2 p-3 border rounded bg-gray-50 space-y-2">
          <select value={type} onChange={e => setType(e.target.value)} className="w-full px-2 py-1 border rounded text-sm">
            <option value="wrong_answer">Səhv cavab</option>
            <option value="unclear">Aydin deyil</option>
            <option value="off_topic">Mövzuya uyğun deyil</option>
            <option value="grammar">Qrammatik sehv</option>
            <option value="other">Diger</option>
          </select>
          <textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="Serh (istege bagli)"
            className="w-full px-2 py-1 border rounded text-sm" rows={2} />
          <button onClick={submit} className="px-3 py-1 bg-red-500 text-white text-sm rounded">Gonder</button>
        </div>
      )}
    </>
  )
}
```

Create `testgen/frontend/src/components/QuestionCard.tsx`:

```tsx
'use client'
import { useState } from 'react'
import LatexRenderer from './LatexRenderer'
import ReportButton from './ReportButton'

interface Props {
  question: {
    question_text: string
    options: Record<string, string> | null
    correct_answer: string
    explanation: string
    latex_content: string | null
    source_reference: string
    bloom_level?: string
    difficulty?: string
  }
  questionId?: string
}

export default function QuestionCard({ question, questionId }: Props) {
  const [showAnswer, setShowAnswer] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-4">
        {question.latex_content ? (
          <LatexRenderer content={question.question_text} />
        ) : (
          <p className="text-lg">{question.question_text}</p>
        )}
      </div>

      {question.options && (
        <div className="space-y-2 mb-4">
          {Object.entries(question.options).map(([key, val]) => (
            <button
              key={key}
              onClick={() => { setSelected(key); setShowAnswer(true) }}
              className={`w-full text-left px-4 py-2 border rounded transition ${
                showAnswer && key === question.correct_answer ? 'bg-green-100 border-green-400' :
                showAnswer && key === selected && key !== question.correct_answer ? 'bg-red-100 border-red-400' :
                selected === key ? 'bg-blue-50 border-blue-400' : 'hover:bg-gray-50'
              }`}
            >
              <span className="font-medium mr-2">{key})</span>
              {question.latex_content ? <LatexRenderer content={val} /> : val}
            </button>
          ))}
        </div>
      )}

      {!question.options && (
        <button onClick={() => setShowAnswer(!showAnswer)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-4">
          {showAnswer ? 'Gizlət' : 'Cavabı göstər'}
        </button>
      )}

      {showAnswer && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <p className="font-medium text-green-700 mb-2">Cavab: {question.correct_answer}</p>
          <p className="text-gray-700 text-sm">{question.explanation}</p>
          <p className="text-gray-400 text-xs mt-2">Menbe: {question.source_reference}</p>
        </div>
      )}

      <div className="mt-4 flex justify-between items-center">
        {questionId && <ReportButton questionId={questionId} />}
        {question.difficulty && (
          <span className={`text-xs px-2 py-1 rounded ${
            question.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
            question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
            'bg-red-100 text-red-700'
          }`}>{question.difficulty}</span>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create generate page**

Create `testgen/frontend/src/app/generate/page.tsx`:

```tsx
'use client'
import { useState } from 'react'
import TopicSelector from '@/components/TopicSelector'
import DifficultyPicker from '@/components/DifficultyPicker'
import QuestionCard from '@/components/QuestionCard'
import { api } from '@/lib/api'

const subjects = [
  { id: 'az_dili', name: 'Azərbaycan dili' },
  { id: 'riyaziyyat', name: 'Riyaziyyat' },
  { id: 'ingilis', name: 'Ingilis dili' },
]

const questionTypes = [
  { id: 'mcq', name: 'Test (5 variant)' },
  { id: 'matching', name: 'Uygunlasma' },
  { id: 'open_ended', name: 'Aciq sual' },
]

export default function GeneratePage() {
  const [subject, setSubject] = useState('az_dili')
  const [grade, setGrade] = useState(9)
  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState('medium')
  const [questionType, setQuestionType] = useState('mcq')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const generate = async () => {
    if (!topic) { setError('Mövzu seçin'); return }
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const res = await api.questions.generate({ subject, grade, topic, difficulty, question_type: questionType })
      setResult(res)
    } catch (err: any) {
      setError(err.message || 'Sual yaratmaq mümkün olmadı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Sual Yarat</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6 space-y-4">
        {/* Subject tabs */}
        <div className="flex gap-2">
          {subjects.map(s => (
            <button key={s.id} onClick={() => { setSubject(s.id); setTopic('') }}
              className={`px-4 py-2 rounded ${subject === s.id ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
              {s.name}
            </button>
          ))}
        </div>

        {/* Grade selector */}
        <div className="flex gap-2">
          {[9, 10, 11].map(g => (
            <button key={g} onClick={() => { setGrade(g); setTopic('') }}
              className={`px-4 py-2 rounded ${grade === g ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
              {g}-cu sinif
            </button>
          ))}
        </div>

        {/* Topic */}
        <TopicSelector subject={subject} grade={grade} value={topic} onChange={setTopic} />

        {/* Difficulty */}
        <div>
          <label className="text-sm font-medium text-gray-600 mb-1 block">Çətinlik</label>
          <DifficultyPicker value={difficulty} onChange={setDifficulty} />
        </div>

        {/* Question type */}
        <div className="flex gap-2">
          {questionTypes.map(qt => (
            <button key={qt.id} onClick={() => setQuestionType(qt.id)}
              className={`px-3 py-1 text-sm rounded ${questionType === qt.id ? 'bg-blue-100 text-blue-700 border border-blue-400' : 'bg-gray-50 text-gray-500 border'}`}>
              {qt.name}
            </button>
          ))}
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button onClick={generate} disabled={loading}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
          {loading ? 'Yaradilir...' : 'Sual Yarat'}
        </button>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-500">Sual yaradilir...</p>
        </div>
      )}

      {result && (
        <div>
          <QuestionCard question={result.question} questionId={result.question_id} />
          <p className="text-xs text-gray-400 mt-2 text-right">
            {result.attempts} cehd | {result.timing.total.toFixed(1)}s
          </p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Verify build**

```bash
cd testgen/frontend && npm run build
```

Expected: Build succeeds.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: student question generation UI with topic selector, difficulty picker, and question card"
```

---

### Task 21: Teacher Panel

**Files:**
- Create: `testgen/frontend/src/app/teacher/dashboard/page.tsx`
- Create: `testgen/frontend/src/app/teacher/generate/page.tsx`
- Create: `testgen/frontend/src/app/teacher/bank/page.tsx`
- Create: `testgen/frontend/src/app/teacher/reports/page.tsx`
- Create: `testgen/frontend/src/app/teacher/export/page.tsx`
- Create: `testgen/frontend/src/components/VariantBuilder.tsx`

- [ ] **Step 1: Create teacher dashboard**

Create `testgen/frontend/src/app/teacher/dashboard/page.tsx`:

```tsx
'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

export default function TeacherDashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    api.stats.dashboard().then(setStats).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Müəllim Paneli</h1>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-2xl font-bold text-blue-600">{stats.total_questions}</p>
            <p className="text-sm text-gray-500">Umumi suallar</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-2xl font-bold text-green-600">{stats.success_rate?.toFixed(1)}%</p>
            <p className="text-sm text-gray-500">Ugur faizi</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-2xl font-bold text-purple-600">{stats.total_generations}</p>
            <p className="text-sm text-gray-500">Umumi generasiyalar</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-2xl font-bold text-orange-600">{stats.avg_generation_time}s</p>
            <p className="text-sm text-gray-500">Ort. vaxt</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link href="/teacher/generate" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <h3 className="font-bold mb-2">Variant Yarat</h3>
          <p className="text-sm text-gray-500">Toplu sual generasiyasi ve variant yaratma</p>
        </Link>
        <Link href="/teacher/bank" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <h3 className="font-bold mb-2">Sual Banki</h3>
          <p className="text-sm text-gray-500">Yaradilmis suallari idareet</p>
        </Link>
        <Link href="/teacher/reports" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <h3 className="font-bold mb-2">Hesabatlar</h3>
          <p className="text-sm text-gray-500">Istifadeci sikavetleri ve duzslisler</p>
        </Link>
        <Link href="/teacher/export" className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
          <h3 className="font-bold mb-2">Ixrac</h3>
          <p className="text-sm text-gray-500">Variantlari PDF/Word/JSON formatinda yukle</p>
        </Link>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create variant builder page**

Create `testgen/frontend/src/components/VariantBuilder.tsx`:

```tsx
'use client'
import { useState } from 'react'
import { api } from '@/lib/api'

export default function VariantBuilder() {
  const [form, setForm] = useState({
    title: '',
    subject: 'az_dili',
    grade: 9,
    total_questions: 25,
    easy: 10,
    medium: 10,
    hard: 5,
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const submit = async () => {
    setError('')
    setLoading(true)
    try {
      const res = await api.variants.generate({
        title: form.title || `Variant - ${new Date().toLocaleDateString('az')}`,
        subject: form.subject,
        grade: form.grade,
        total_questions: form.easy + form.medium + form.hard,
        difficulty_dist: { easy: form.easy, medium: form.medium, hard: form.hard },
      })
      setResult(res)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-4">
      <input type="text" placeholder="Variant adi" value={form.title}
        onChange={e => setForm({ ...form, title: e.target.value })}
        className="w-full px-4 py-2 border rounded" />

      <div className="grid grid-cols-2 gap-4">
        <select value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })}
          className="px-4 py-2 border rounded">
          <option value="az_dili">Azərbaycan dili</option>
          <option value="riyaziyyat">Riyaziyyat</option>
          <option value="ingilis">Ingilis dili</option>
        </select>
        <select value={form.grade} onChange={e => setForm({ ...form, grade: Number(e.target.value) })}
          className="px-4 py-2 border rounded">
          <option value={9}>9-cu sinif</option>
          <option value={10}>10-cu sinif</option>
          <option value={11}>11-ci sinif</option>
        </select>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-600 mb-2">Çətinlik bölgüsü</p>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-green-600">Asan</label>
            <input type="number" min={0} value={form.easy}
              onChange={e => setForm({ ...form, easy: Number(e.target.value) })}
              className="w-full px-3 py-1 border rounded" />
          </div>
          <div>
            <label className="text-xs text-yellow-600">Orta</label>
            <input type="number" min={0} value={form.medium}
              onChange={e => setForm({ ...form, medium: Number(e.target.value) })}
              className="w-full px-3 py-1 border rounded" />
          </div>
          <div>
            <label className="text-xs text-red-600">Cetin</label>
            <input type="number" min={0} value={form.hard}
              onChange={e => setForm({ ...form, hard: Number(e.target.value) })}
              className="w-full px-3 py-1 border rounded" />
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-1">Cemi: {form.easy + form.medium + form.hard} sual</p>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button onClick={submit} disabled={loading}
        className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
        {loading ? 'Yaradilir... (bu bir nece deqiqe ceke biler)' : 'Variant Yarat'}
      </button>

      {result && (
        <div className="p-4 bg-green-50 rounded">
          <p className="text-green-700 font-medium">Variant yaradildi!</p>
          <p className="text-sm text-gray-500">ID: {result.id}</p>
        </div>
      )}
    </div>
  )
}
```

Create `testgen/frontend/src/app/teacher/generate/page.tsx`:

```tsx
import VariantBuilder from '@/components/VariantBuilder'

export default function TeacherGeneratePage() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Variant Yarat</h1>
      <VariantBuilder />
    </div>
  )
}
```

- [ ] **Step 3: Create question bank page**

Create `testgen/frontend/src/app/teacher/bank/page.tsx`:

```tsx
'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { Question } from '@/lib/types'

export default function QuestionBankPage() {
  const [questions, setQuestions] = useState<Question[]>([])
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({ subject: '', difficulty: '', page: 1 })

  useEffect(() => {
    const params = new URLSearchParams()
    if (filters.subject) params.set('subject', filters.subject)
    if (filters.difficulty) params.set('difficulty', filters.difficulty)
    params.set('page', String(filters.page))
    params.set('page_size', '20')

    api.questions.list(params.toString())
      .then(res => { setQuestions(res.items); setTotal(res.total) })
      .catch(() => {})
  }, [filters])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Sual Banki ({total})</h1>

      <div className="flex gap-4 mb-6">
        <select value={filters.subject} onChange={e => setFilters({ ...filters, subject: e.target.value, page: 1 })}
          className="px-3 py-2 border rounded">
          <option value="">Butun fennler</option>
          <option value="az_dili">Azərbaycan dili</option>
          <option value="riyaziyyat">Riyaziyyat</option>
          <option value="ingilis">Ingilis dili</option>
        </select>
        <select value={filters.difficulty} onChange={e => setFilters({ ...filters, difficulty: e.target.value, page: 1 })}
          className="px-3 py-2 border rounded">
          <option value="">Butun cetinlikler</option>
          <option value="easy">Asan</option>
          <option value="medium">Orta</option>
          <option value="hard">Cetin</option>
        </select>
      </div>

      <div className="space-y-3">
        {questions.map(q => (
          <div key={q.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start">
              <p className="flex-1">{q.question_text.slice(0, 150)}...</p>
              <span className={`ml-2 text-xs px-2 py-1 rounded ${
                q.status === 'active' ? 'bg-green-100 text-green-700' :
                q.status === 'reported' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>{q.status}</span>
            </div>
            <div className="flex gap-2 mt-2 text-xs text-gray-400">
              <span>{q.subject}</span>
              <span>{q.grade}-ci sinif</span>
              <span>{q.topic}</span>
              <span>{q.difficulty}</span>
            </div>
          </div>
        ))}
      </div>

      {total > 20 && (
        <div className="flex justify-center gap-2 mt-6">
          <button onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
            disabled={filters.page <= 1} className="px-3 py-1 border rounded disabled:opacity-50">Evvelki</button>
          <span className="px-3 py-1">{filters.page}</span>
          <button onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
            disabled={filters.page * 20 >= total} className="px-3 py-1 border rounded disabled:opacity-50">Novbeti</button>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create reports page**

Create `testgen/frontend/src/app/teacher/reports/page.tsx`:

```tsx
'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [filter, setFilter] = useState('pending')

  useEffect(() => {
    api.reports.list(filter).then(setReports).catch(() => {})
  }, [filter])

  const resolve = async (id: string, status: string) => {
    await api.reports.resolve(id, status)
    setReports(reports.filter(r => r.id !== id))
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Hesabatlar</h1>

      <div className="flex gap-2 mb-6">
        {['pending', 'fixed', 'rejected'].map(s => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded ${filter === s ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
            {s === 'pending' ? 'Gozleyir' : s === 'fixed' ? 'Duzeldildi' : 'Redd edildi'}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {reports.map(r => (
          <div key={r.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between">
              <div>
                <p className="font-medium">{r.report_type}</p>
                {r.comment && <p className="text-sm text-gray-500">{r.comment}</p>}
                <p className="text-xs text-gray-400">Sual: {r.question_id}</p>
              </div>
              {filter === 'pending' && (
                <div className="flex gap-2">
                  <button onClick={() => resolve(r.id, 'fixed')}
                    className="px-3 py-1 bg-green-500 text-white text-sm rounded">Duzelt</button>
                  <button onClick={() => resolve(r.id, 'rejected')}
                    className="px-3 py-1 bg-red-500 text-white text-sm rounded">Redd et</button>
                </div>
              )}
            </div>
          </div>
        ))}
        {reports.length === 0 && <p className="text-gray-400 text-center py-8">Hesabat yoxdur</p>}
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Create export page**

Create `testgen/frontend/src/app/teacher/export/page.tsx`:

```tsx
'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function ExportPage() {
  const [variants, setVariants] = useState<any[]>([])

  useEffect(() => {
    api.variants.list().then(setVariants).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Ixrac</h1>
      <div className="space-y-3">
        {variants.map(v => (
          <div key={v.id} className="bg-white rounded-lg shadow p-4 flex justify-between items-center">
            <div>
              <p className="font-medium">{v.title}</p>
              <p className="text-sm text-gray-500">{v.subject} | {v.total_questions} sual</p>
            </div>
            <div className="flex gap-2">
              <a href={api.variants.export(v.id, 'json')} download
                className="px-3 py-1 bg-blue-500 text-white text-sm rounded">JSON</a>
              <a href={api.variants.export(v.id, 'text')} download
                className="px-3 py-1 bg-green-500 text-white text-sm rounded">TXT</a>
            </div>
          </div>
        ))}
        {variants.length === 0 && <p className="text-gray-400 text-center py-8">Variant yoxdur</p>}
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Create dashboard redirect page**

Create `testgen/frontend/src/app/dashboard/page.tsx`:

```tsx
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (!user) { router.push('/login'); return }
    router.push(user.role === 'teacher' ? '/teacher/dashboard' : '/generate')
  }, [user, loading, router])

  return <div className="text-center py-8">Yonlendirilir...</div>
}
```

- [ ] **Step 7: Verify build**

```bash
cd testgen/frontend && npm run build
```

Expected: Build succeeds.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: teacher panel with dashboard, variant builder, question bank, reports, and export"
```

---

## Phase 7: Integration & Deployment

### Task 22: End-to-End Smoke Test

**Files:**
- Modify: `testgen/backend/tests/conftest.py`

- [ ] **Step 1: Run full backend test suite**

```bash
cd testgen/backend
pytest tests/ -v --tb=short
```

Expected: All tests pass. If any fail, fix them before proceeding.

- [ ] **Step 2: Start full stack and verify**

```bash
cd testgen
docker compose up --build -d
```

Wait for all services to start, then:

```bash
# Health check
curl http://localhost:8000/health

# Subjects list
curl http://localhost:8000/api/subjects

# Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

Expected:
- Backend health: `{"status":"ok"}`
- Subjects: JSON array with 3 subjects
- Frontend: HTTP 200

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test: verify full stack smoke test passes"
```

---

### Task 23: Render Deployment Configuration

**Files:**
- Create: `testgen/render.yaml`

- [ ] **Step 1: Create Render blueprint**

Create `testgen/render.yaml`:

```yaml
services:
  - type: web
    name: testgen-backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: testgen-db
          property: connectionString
        # Note: Replace postgresql:// with postgresql+asyncpg:// in config.py for async
      - key: QDRANT_URL
        fromService:
          name: testgen-qdrant
          type: pserv
          property: hostport
      - key: GEMINI_API_KEY
        sync: false
      - key: JWT_SECRET
        generateValue: true
    healthCheckPath: /health

  - type: web
    name: testgen-frontend
    runtime: node
    buildCommand: cd frontend && npm install && npm run build
    startCommand: cd frontend && npm start
    envVars:
      - key: NEXT_PUBLIC_API_URL
        value: https://testgen-backend.onrender.com

  - type: pserv
    name: testgen-qdrant
    runtime: docker
    dockerfilePath: ./Dockerfile.qdrant
    disk:
      name: qdrant-data
      mountPath: /qdrant/storage
      sizeGB: 1

databases:
  - name: testgen-db
    databaseName: testgen
    user: testgen
    plan: free  # Note: Render free PostgreSQL expires after 30 days → upgrade to starter ($7/mo)
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "chore: Render deployment blueprint"
```

---

## Final: Complete main.py Reference

After all tasks, `testgen/backend/main.py` should look like:

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from auth.security import get_current_user
from auth.router import router as auth_router
from generation.router import router as generation_router
from questions.router import router as questions_router
from subjects.router import router as subjects_router
from variants.router import router as variants_router
from reports.router import router as reports_router
from models.user import User
from models.question import Question
from models.generation_log import GenerationLog

app = FastAPI(title="TestGen AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(generation_router)
app.include_router(questions_router)
app.include_router(subjects_router)
app.include_router(variants_router)
app.include_router(reports_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/stats/dashboard")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_questions = (await db.execute(select(func.count(Question.id)))).scalar() or 0
    total_generations = (await db.execute(select(func.count(GenerationLog.id)))).scalar() or 0
    success_count = (await db.execute(
        select(func.count(GenerationLog.id)).where(GenerationLog.success == True)
    )).scalar() or 0
    avg_time = (await db.execute(select(func.avg(GenerationLog.total_time)))).scalar() or 0

    return {
        "total_questions": total_questions,
        "total_generations": total_generations,
        "success_rate": (success_count / total_generations * 100) if total_generations > 0 else 0,
        "avg_generation_time": round(avg_time, 2),
    }
```

---

## Summary

| Phase | Tasks | What it delivers |
|-------|-------|-----------------|
| 1. Foundation | 1-3 | Docker stack, DB schema, FastAPI shell |
| 2. Auth & Clients | 4-6 | JWT auth, Gemini wrapper, Qdrant wrapper |
| 3. Data Pipeline | 7-10 | PDF parsing, TOC extraction, chunking, indexing CLI |
| 4. Generation Engine | 11-14 | 3-stage RAG pipeline with API endpoint |
| 5. REST API | 15-18B | Question CRUD, topics, variants, reports, stats |
| 6. Frontend | 19-21 | Complete Next.js app with student + teacher UIs |
| 7. Deployment | 22-23 | Smoke tests, Render config |

**Total: 23 tasks, ~120 steps**
