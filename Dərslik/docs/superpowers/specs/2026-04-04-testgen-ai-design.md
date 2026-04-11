# TestGen AI — System Design Specification

**Title:** An Intelligent AI-Based System for Automatic Generation of Test Cases from Methodological Resources

**Date:** 2026-04-04
**Author:** Master's Dissertation + Ultra Company Product
**Status:** Approved

---

## 1. Problem Statement

In Azerbaijan, the State Examination Center (DIM) publishes new test booklets annually for university entrance exams with minimal changes — questions are rearranged, a small number of new questions are added, and the cover is changed. Families with multiple children are forced to repurchase nearly identical booklets at 15-20 AZN each year.

There is no AI-based test question generation system implemented in Azerbaijan. This project addresses this gap by building a web application that generates unique, curriculum-grounded test questions using a RAG (Retrieval-Augmented Generation) pipeline.

## 2. Scope

### In Scope (MVP / Phase 1)
- **Exam:** 300-point first stage of DIM university entrance exam
- **Subjects:** Azerbaijani language, Mathematics, English language
- **Grades:** 9, 10, 11
- **Question types:** Multiple choice (5 options), matching, open-ended
- **Users:** Students (abituriyent) + Teachers
- **Language:** Azerbaijani (architecture is multi-language ready)
- **Authentication:** Email + Google OAuth, role-based (student/teacher)
- **Monetization:** None in MVP

### Out of Scope (Phase 2)
- 400-point second stage subjects (Physics, Chemistry, Biology, History, etc.)
- Russian language support
- API layer for education platform integration
- Teacher approval workflow for question bank
- Payment/subscription system
- Agent-based pipeline architecture

## 3. Source Materials

### Available
| Material | Format | Status |
|----------|--------|--------|
| Textbooks (grades 9-11, 11 subjects) | PDF (up to ~95MB) | On hand |
| DIM exam programs (syllabi) | PDF | Free on dim.gov.az |

### To Be Acquired
| Material | Format | Source |
|----------|--------|--------|
| DIM test collections (Az dili, Math, English) | PDF | Scribd, Telegram, internet |
| Past 300-point entrance exam papers | PDF | dim.gov.az, azfizik.blogspot.com |
| DIM practice exam variants (20 variant books) | PDF | Online sources |

## 4. Technology Stack

| Component | Technology | Version/Details |
|-----------|-----------|-----------------|
| LLM | Gemini 3 Flash | Released Dec 2025. Model ID: `gemini-3-flash-preview`. $0.50/1M input, $3/1M output. 1M token context. Outperforms 2.5 Pro at 3x speed. |
| Embedding | Gemini Embedding 2 | Public preview Mar 10, 2026 (not yet GA — API may change before general availability). Model ID: `gemini-embedding-2-preview`. First natively multimodal embedding. 3072-dim vectors. MRL support. MTEB #1. |
| Vector DB | Qdrant v1.16 | Local/remote. Inline storage, multitenancy. |
| Backend | FastAPI (Python) | Gemini SDK Python support |
| Frontend | Next.js + React | App Router, Tailwind CSS |
| User DB | PostgreSQL 16 | Users, question bank, statistics |
| Math Rendering | KaTeX | LaTeX formula rendering in frontend |
| Diagram Generation | Matplotlib/TikZ | Simple geometric diagrams for math |
| Deployment | Render + Docker | Docker Compose for local dev |

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│                   (Next.js + React)                       │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Auth UI  │  │ Sual Gen. UI │  │ Teacher Panel UI  │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API
┌──────────────────────▼───────────────────────────────────┐
│                      BACKEND                              │
│                  (FastAPI + Python)                        │
│                                                           │
│  ┌─────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │Auth     │  │Question Gen. │  │Question Bank        │  │
│  │Service  │  │Pipeline      │  │Service              │  │
│  └─────────┘  └──────┬───────┘  └─────────────────────┘  │
│                      │                                    │
│         ┌────────────┼────────────┐                       │
│         ▼            ▼            ▼                       │
│  ┌────────────┐ ┌─────────┐ ┌──────────┐                 │
│  │Retrieval   │ │Generate │ │Validate  │                  │
│  │Stage       │ │Stage    │ │Stage     │                  │
│  └──────┬─────┘ └────┬────┘ └────┬─────┘                 │
└─────────┼────────────┼───────────┼────────────────────────┘
          │            │           │
    ┌─────▼─────┐ ┌────▼────┐ ┌───▼────┐
    │  Qdrant   │ │Gemini 3 │ │Qdrant  │
    │(2 collec.)│ │ Flash   │ │+Gemini │
    └───────────┘ └─────────┘ └────────┘

    ┌───────────┐
    │PostgreSQL │ ← Users, question bank, statistics
    └───────────┘
```

## 6. Data Pipeline

### 6.1 Textbook Processing

1. **PDF Parsing:** Gemini 3 Flash natively reads PDFs (no OCR needed). Pages processed in batches (large PDFs up to ~95MB). Note: Gemini API inline PDF limit is 50MB — files exceeding this use the Files API (`client.files.upload()`).
2. **TOC Extraction:** Gemini extracts the table of contents to build a topic hierarchy per textbook.
3. **Hybrid Chunking:** Topic-based splitting from TOC, then page-based sub-chunking for large topics. Target chunk size: 500-1500 tokens.
4. **Metadata Attachment:** Each chunk tagged with: subject, grade, chapter, topic, subtopic, pages, source type.
5. **Embedding:** Gemini Embedding 2 generates 3072-dim vectors per chunk.
6. **Indexing:** Vectors stored in Qdrant `textbooks` collection.

### 6.2 DIM Test Material Processing

1. **Question Parsing:** Gemini 3 Flash extracts individual questions from DIM PDFs with structured output: question text, options, correct answer, topic, estimated difficulty, year, source type, image descriptions.
2. **Embedding:** Each question embedded as a single unit.
3. **Indexing:** Vectors stored in Qdrant `dim_tests` collection.

### 6.3 Pipeline Execution

The data pipeline runs locally as a CLI script. PDFs are not uploaded to the server. Only the resulting vectors are sent to the remote Qdrant instance.

```
Local computer                    Render
┌──────────────┐                 ┌──────────┐
│ run_pipeline │ ──── HTTPS ───→ │ Qdrant   │
│ + PDF files  │                 │ (remote) │
└──────────────┘                 └──────────┘
```

### 6.4 Math-Specific Handling

Math textbook chunks include LaTeX representations of formulas alongside text content and image descriptions, ensuring the LLM uses correct mathematical notation during generation.

## 7. Question Generation Pipeline (Core Engine)

### 7.1 Three-Stage Flow

```
User selects: subject + grade + topic + difficulty + question_type
                    │
                    ▼
    ┌───────────────────────────────┐
    │ STAGE 1: CONTEXT RETRIEVAL    │
    │                               │
    │ 1A: Qdrant "textbooks"        │
    │   filter: subject, grade,     │
    │   topic → Top 5 chunks        │
    │   (what the student learned)  │
    │                               │
    │ 1B: Qdrant "dim_tests"        │
    │   filter: subject, topic,     │
    │   question_type → Top 5       │
    │   example questions           │
    │   (how DIM asks questions)    │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │ STAGE 2: GENERATION           │
    │                               │
    │ Gemini 3 Flash receives:      │
    │ - System prompt (expert role) │
    │ - Textbook context            │
    │ - DIM example questions       │
    │ - Task: topic, Bloom level,   │
    │   format, constraints         │
    │                               │
    │ Output: structured JSON with  │
    │ question, options, answer,    │
    │ explanation, source reference │
    └───────────────┬───────────────┘
                    ▼
    ┌───────────────────────────────┐
    │ STAGE 3: VALIDATION           │
    │                               │
    │ 3A: Semantic Similarity       │
    │   Embed generated question    │
    │   → search dim_tests          │
    │   → if similarity > 0.85     │
    │     → REJECT                  │
    │                               │
    │ 3B: LLM Self-Validation       │
    │   Second Gemini call checks:  │
    │   1. Answer correctness       │
    │   2. Textbook alignment       │
    │   3. Originality              │
    │   4. Bloom level accuracy     │
    │   5. Grammar quality          │
    │                               │
    │   PASS → return + save to DB  │
    │   FAIL → retry Stage 2       │
    │          (max 3 attempts)     │
    └───────────────────────────────┘
```

### 7.2 Difficulty-Bloom Mapping

| User Selects | LLM Prompt Bloom Level |
|---|---|
| Easy | Remember + Understand |
| Medium | Apply + Analyze |
| Hard | Evaluate + Create |

> **Note:** Uses Anderson & Krathwohl's revised Bloom taxonomy (2001), which is the current academic standard. The original 1956 taxonomy used different terminology (Knowledge, Comprehension, Application, Analysis, Synthesis, Evaluation).

### 7.3 Bulk Generation (Teacher)

Teacher selects subject, grades, total questions, difficulty distribution, and topic distribution (auto/manual). "Auto" mode distributes questions across topics proportionally to how often each topic appears in the `dim_tests` collection (i.e., mirroring DIM's actual exam distribution). Backend runs the same pipeline in parallel (5 concurrent) to generate the full variant. Output exported as PDF/Word/JSON.

## 8. Frontend Design

### 8.1 Student Interface
- Subject tabs (Az dili / Riyaziyyat / English)
- Grade selector (9 / 10 / 11)
- Topic dropdown (populated from textbook TOC)
- Difficulty picker (Easy / Medium / Hard)
- Question type selector (MCQ / Matching / Open-ended)
- "Generate" button → question card with answer reveal, explanation, source reference
- "Report Error" button per question

### 8.2 Teacher Panel
- Left sidebar menu: Generate / Variants / Question Bank / Reports / Export
- Variant builder: subject, grades, question count, difficulty distribution sliders, topic distribution (auto DIM ratio or manual)
- Question bank: searchable, filterable list with status indicators
- Report management: view reported questions → Edit / Delete / Reject report
- Export: PDF / Word / JSON

### 8.3 Routes
```
/                    → Landing page
/login               → Login (email + Google)
/register            → Registration (role selection)
/dashboard           → User dashboard
/generate            → Question generation (student)
/teacher/dashboard   → Teacher panel
/teacher/generate    → Bulk generation
/teacher/bank        → Question bank management
/teacher/reports     → Error reports + corrections
/teacher/export      → Export (PDF/Word)
```

## 9. Database Schema

### 9.1 PostgreSQL Tables

**users**
- id (UUID PK), email (UNIQUE), password_hash (nullable), full_name, role (student/teacher), auth_provider (email/google), created_at, last_login

**questions**
- id (UUID PK), subject, grade, topic, subtopic, question_type (mcq/matching/open_ended), difficulty (easy/medium/hard), bloom_level, question_text, question_image (nullable), options (JSONB, nullable), matching_pairs (JSONB, nullable), correct_answer, explanation, latex_content (nullable), source_reference, similarity_score, validation_result (JSONB), status (active/reported/disabled/edited), created_by (FK users), created_at, times_served, report_count

**variants**
- id (UUID PK), title, subject, total_questions, difficulty_dist (JSONB), created_by (FK users), created_at

**variant_questions**
- variant_id (FK variants), question_id (FK questions), order_number

**reports**
- id (UUID PK), question_id (FK questions), reported_by (FK users), report_type (wrong_answer/unclear/off_topic/duplicate/grammar/other), comment, status (pending/fixed/rejected), created_at

**generation_logs**
- id (UUID PK), user_id (FK users), question_id (FK questions, nullable), subject, topic, difficulty, retrieval_time, generation_time, validation_time, total_time, attempts, success, token_usage (JSONB), created_at

### 9.2 PostgreSQL — Topic Tree Cache

**topics** (derived from textbook TOC during data pipeline, cached in PostgreSQL for fast API access)
- id (UUID PK), subject, grade, chapter, chapter_order, topic, subtopic, page_start, page_end

This table powers `GET /api/subjects/:id/topics` — the frontend topic dropdown. Populated during data pipeline indexing, not at runtime.

### 9.3 Qdrant Collections

Both collections use **cosine similarity** metric for vector search.

**textbooks** — payload: subject, grade, chapter, topic, subtopic, pages, text_content, has_image, image_description, latex

**dim_tests** — payload: subject, topic, question_type, difficulty_estimated, question_text, options, correct_answer, year, source_type, has_image

## 10. API Endpoints

### Auth
- `POST /api/auth/register` — Registration
- `POST /api/auth/login` — Login (returns JWT)
- `POST /api/auth/google` — Google OAuth callback
- `GET /api/auth/me` — Current user profile

### Question Generation
- `POST /api/questions/generate` — Generate single question

### Question Bank
- `GET /api/questions` — List questions (filter + pagination)
- `GET /api/questions/:id` — Single question
- `PATCH /api/questions/:id` — Edit question (teacher)
- `DELETE /api/questions/:id` — Delete question (teacher)

### Variants
- `POST /api/variants/generate` — Generate bulk variant (teacher)
- `GET /api/variants` — List variants
- `GET /api/variants/:id` — Variant detail
- `GET /api/variants/:id/export` — Export (format: pdf/word/json)

### Reports
- `POST /api/reports` — Report error
- `GET /api/reports` — List reports (teacher)
- `PATCH /api/reports/:id` — Resolve report (fixed/rejected)

### Metadata
- `GET /api/subjects` — Subject list
- `GET /api/subjects/:id/topics` — Topic tree (from TOC)
- `GET /api/stats/dashboard` — Statistics

## 11. Project Structure

```
testgen/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── auth/           (router, service, models, schemas)
│   ├── questions/      (router, service, models, schemas)
│   ├── generation/
│   │   ├── router.py
│   │   ├── pipeline.py       ← 3-stage orchestrator
│   │   ├── retrieval.py      ← Stage 1: Qdrant queries
│   │   ├── generator.py      ← Stage 2: Gemini generation
│   │   ├── validator.py      ← Stage 3: Validation
│   │   └── prompts.py        ← All LLM prompts centralized
│   ├── variants/       (router, service, export)
│   ├── core/
│   │   ├── database.py       ← PostgreSQL connection
│   │   ├── qdrant_client.py  ← Qdrant connection
│   │   ├── gemini_client.py  ← Gemini API wrapper
│   │   ├── embedding.py      ← Gemini Embedding 2 wrapper
│   │   └── dependencies.py   ← FastAPI dependencies
│   └── data_pipeline/
│       ├── pdf_processor.py  ← Gemini PDF parsing
│       ├── toc_extractor.py  ← TOC extraction
│       ├── chunker.py        ← Hybrid chunking
│       ├── dim_parser.py     ← DIM question parsing
│       ├── indexer.py        ← Qdrant indexing
│       └── run_pipeline.py   ← CLI entry point
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/              ← Pages (routes as listed above)
│   │   ├── components/
│   │   │   ├── QuestionCard.tsx
│   │   │   ├── GenerateForm.tsx
│   │   │   ├── TopicSelector.tsx
│   │   │   ├── DifficultyPicker.tsx
│   │   │   ├── VariantBuilder.tsx
│   │   │   ├── QuestionEditor.tsx
│   │   │   ├── ReportButton.tsx
│   │   │   ├── ExportDialog.tsx
│   │   │   └── LatexRenderer.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── types.ts
│   │   └── styles/globals.css
│
└── data/                      ← Git-ignored
    ├── textbooks/
    │   ├── sinif9/
    │   ├── sinif10/
    │   └── sinif11/
    └── dim_tests/
        ├── az_dili/
        ├── riyaziyyat/
        └── ingilis/
```

## 12. Deployment

### Local Development
Docker Compose with 4 services: backend (FastAPI), frontend (Next.js), db (PostgreSQL 16), qdrant (Qdrant latest).

### Production (Render)
| Service | Render Type | Plan | Est. Cost |
|---------|------------|------|-----------|
| testgen-backend | Web Service (Docker) | Starter | ~$7/mo |
| testgen-frontend | Web Service (Node) | Free/Starter | $0-7/mo |
| testgen-db | PostgreSQL | Free (30 days) → Starter | $0-7/mo |
| testgen-qdrant | Private Service (Docker) | Starter | ~$7/mo |

**Estimated monthly cost:** $14-21 + Gemini API (~$5-10 based on usage)

### Environment Variables
- `GEMINI_API_KEY` — Gemini API key
- `DATABASE_URL` — PostgreSQL connection string
- `QDRANT_URL` — Qdrant endpoint
- `JWT_SECRET` — JWT signing secret
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — Google OAuth
- `SIMILARITY_THRESHOLD` — Default 0.85 (cosine similarity; 1.0 = identical, 0.0 = unrelated)
- `MAX_GENERATION_ATTEMPTS` — Default 3

## 13. Evaluation Methodology (Dissertation)

### 13.1 Question Quality (Expert Review)
3-5 teachers evaluate 50 generated questions per subject on a 1-5 scale across: scientific correctness, curriculum alignment, language quality, difficulty adequacy, DIM format compliance. Metrics: mean score, Cohen's Kappa.

### 13.2 Uniqueness (Automated)
100 questions per subject. Metrics: mean similarity score to DIM questions, similarity distribution, percentage exceeding 0.85 threshold, inter-generation similarity, LLM originality PASS/FAIL ratio.

### 13.3 Bloom Taxonomy Accuracy
30 questions per difficulty level (90 total). Experts independently classify Bloom level. Metrics: confusion matrix, accuracy, Kappa score.

### 13.4 System Performance (Automated)
From generation_logs table. Metrics: mean response time, per-stage time breakdown, first-attempt PASS rate, mean retry count, token cost per question, per-subject comparison.

### 13.5 Baseline Comparison (Traditional vs AI)

| Criteria | Traditional (Teacher) | Our System (AI) |
|---|---|---|
| 1 question creation time | 10-30 minutes | 3-5 seconds |
| 25-question variant | 4-8 hours | 2-3 minutes |
| Cost per variant | ~50-100 AZN | ~0.05 AZN |
| Uniqueness verification | Subjective | Quantitative (similarity %) |
| Bloom alignment | Depends on experience | Systematic mapping |
| Scalability | Linear (more = more cost) | Nearly unlimited |
| Quality | High (experienced teacher) | Medium-High (with validation) |
| Availability | Teacher required | 24/7 anywhere |

## 14. Novel Contributions

1. **Methodological:** First RAG-based test question generation pipeline for Azerbaijan's education system context.
2. **Technical:** Dual-layer originality verification (semantic similarity + LLM-based assessment).
3. **Applied:** Working web application grounded in real DIM materials and official textbooks, first implementation in Azerbaijan.
4. **Evaluative:** Multi-dimensional evaluation framework for LLM-generated test questions.

## 15. Dissertation Chapter Structure

1. **Introduction** — Problem, relevance, goal, scientific novelty
2. **Literature Review** — LLM-based question generation, RAG architecture, Bloom's taxonomy in education, Azerbaijan education system and DIM
3. **Methodology** — Multi-stage RAG pipeline design, Bloom mapping approach, dual-layer originality verification, technology choice justification
4. **System Implementation** — Architecture, data pipeline, question generation pipeline, frontend/backend
5. **Experiments and Results** — 4 evaluation dimensions, baseline comparison, statistical analysis
6. **Conclusion and Recommendations** — Results, limitations, future work (Phase 2)
