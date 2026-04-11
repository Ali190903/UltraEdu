import asyncio
import io
import json
import random
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from google import genai
from google.genai import types

from data_pipeline.json_utils import parse_llm_json

LLM_MODEL = "gemini-3-flash-preview"

# DIM Riyaziyyat I hissə — chapter map (0-indexed PDF page ranges, end exclusive)
# PDF page = book page - 2  |  0-indexed = PDF page - 1
DIM_RIYAZIYYAT_1_CHAPTERS = [
    {"id": "ch01",    "name": "Natural ədədlər",                               "start": 1,   "end": 10},
    {"id": "ch02",    "name": "Adi və onluq kəsrlər",                          "start": 10,  "end": 17},
    {"id": "ch03",    "name": "Faiz. Nisbət. Tənasüb",                         "start": 17,  "end": 28},
    {"id": "ch04",    "name": "Həqiqi ədədlər",                                "start": 28,  "end": 33},
    {"id": "ch05",    "name": "Tam cəbri ifadələr",                            "start": 33,  "end": 38},
    {"id": "ch06",    "name": "Çoxhədlinin vuruqlara ayrılması",                "start": 38,  "end": 44},
    {"id": "ch07",    "name": "Rasional kəsrlər",                              "start": 44,  "end": 52},
    {"id": "ch08",    "name": "Kvadrat köklər. Həqiqi üstlü qüvvət",           "start": 52,  "end": 65},
    {"id": "ch09",    "name": "Birməchullu tənliklər və məsələlər",            "start": 65,  "end": 83},
    {"id": "ch10",    "name": "Tənliklər sistemi",                             "start": 83,  "end": 94},
    {"id": "ch11",    "name": "Bərabərsizliklər və bərabərsizliklər sistemi",  "start": 94,  "end": 110},
    {"id": "ch12",    "name": "Ədədi ardıcıllıqlar. Silsilələr",               "start": 110, "end": 126},
    {"id": "ch13",    "name": "Çoxluqlar",                                     "start": 126, "end": 132},
    {"id": "ch14",    "name": "Həndəsənin əsas anlayışları",                   "start": 132, "end": 141},
    {"id": "ch15",    "name": "Üçbucaqlar",                                    "start": 141, "end": 159},
    {"id": "ch16",    "name": "Çoxbucaqlılar. Dördbucaqlılar",                 "start": 159, "end": 170},
    {"id": "ch17",    "name": "Çevrə və dairə",                                "start": 170, "end": 191},
    {"id": "ch18",    "name": "İsbat məsələləri",                              "start": 191, "end": 194},
    {"id": "ch19",    "name": "Situasiya",                                     "start": 194, "end": 204},
    {"id": "imtahan", "name": "İmtahan sualları (2025)",                       "start": 204, "end": 210},
]

ANSWER_KEY_START = 210
ANSWER_KEY_END   = 231


def extract_pages_bytes(pdf_path: str, start: int, end: int) -> bytes:
    """Return bytes of pages [start, end) from PDF (0-indexed)."""
    doc = fitz.open(pdf_path)
    out = fitz.open()
    out.insert_pdf(doc, from_page=start, to_page=end - 1)
    buf = io.BytesIO()
    out.save(buf)
    return buf.getvalue()


def combine_pdf_bytes(bytes1: bytes, bytes2: bytes) -> bytes:
    """Append bytes2 pages after bytes1 pages and return combined bytes."""
    doc1 = fitz.open(stream=bytes1, filetype="pdf")
    doc2 = fitz.open(stream=bytes2, filetype="pdf")
    out = fitz.open()
    out.insert_pdf(doc1)
    out.insert_pdf(doc2)
    buf = io.BytesIO()
    out.save(buf)
    return buf.getvalue()


class DimParser:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def _call_gemini(self, contents, json_mode: bool = True, timeout: int = 60) -> str:
        """Gemini API call with unlimited retry for capacity/rate errors."""
        config = types.GenerateContentConfig(
            max_output_tokens=65536,
            temperature=0.0,
        )
        if json_mode:
            config.response_mime_type = "application/json"

        RETRYABLE = ("429", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "high demand", "overloaded", "No capacity")
        CALL_TIMEOUT = timeout
        attempt = 0
        while True:
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=LLM_MODEL,
                        contents=contents,
                        config=config,
                    ),
                    timeout=CALL_TIMEOUT,
                )
                if response.text is None:
                    attempt += 1
                    delay = min(5 * attempt, 20)
                    print(f"      [Retry #{attempt}] empty response, waiting {delay}s...", flush=True)
                    await asyncio.sleep(delay)
                    continue
                return response.text
            except (asyncio.TimeoutError, asyncio.CancelledError):
                attempt += 1
                delay = int(10 * (0.8 + 0.4 * random.random()))
                print(f"      [Retry #{attempt}] timeout ({CALL_TIMEOUT}s), waiting {delay}s...", flush=True)
                await asyncio.sleep(delay)
            except Exception as e:
                err = str(e)
                if any(x in err for x in RETRYABLE):
                    attempt += 1
                    base = min(5 * attempt, 20)
                    delay = int(base * (0.8 + 0.4 * random.random()))
                    print(f"      [Retry #{attempt}] model busy, waiting {delay}s... ({err[:60]})", flush=True)
                    await asyncio.sleep(delay)
                else:
                    raise

    async def _pass1_extract(self, chapter_pdf_bytes: bytes, chapter_name: str) -> list[dict]:
        """Pass 1: Extract one representative question per unique archetype."""
        prompt = f"""This PDF contains questions from the "{chapter_name}" chapter of a DIM (Dövlət İmtahan Mərkəzi) math test booklet (2025).

TASK: Extract ONE representative question per unique question archetype. Do NOT solve them yet.

DEDUPLICATION RULE (most important):
- Many questions in this book test the same mathematical concept with only different numbers (e.g. same formula $\\overline{{ab}} = 2a+4b$ vs $\\overline{{ab}} = 3a+5b$, or same logic $(7a-3)^2$ tək vs $(3x-1)^2$ cüt).
- These are the SAME archetype. Extract only ONE of them — the clearest/most representative example.
- Two questions are the SAME archetype if they require the exact same mathematical reasoning/method to solve, regardless of the numbers used.
- Two questions are DIFFERENT archetypes if they require a genuinely different mathematical concept, formula, or reasoning strategy.

For each UNIQUE archetype extract:
- question_text: full text in Azerbaijani, LaTeX for math: $x^2$, $\\frac{{a}}{{b}}$, $\\overline{{ab}}$, $\\sqrt{{x}}$
- options: {{"A":"...","B":"...","C":"...","D":"...","E":"..."}} for MCQ; null for open_ended
- subtopic: section heading printed above this question group in Azerbaijani
- question_type: "mcq" or "open_ended"
- has_image: true ONLY if a figure, diagram, coordinate system or data table is needed
- image_description: describe visible numbers/labels if has_image true; null otherwise

Include ALL genuinely different question types:
- MCQ, open_ended, matching (uyğunluğu müəyyən edin) — each archetype once
- Questions with images (mark has_image: true) — each visual archetype once

Target: 25-40 unique archetypes per chapter (not 150+).

Return ONLY a valid JSON array:
[{{"question_text":"...","options":{{"A":"...","B":"...","C":"...","D":"...","E":"..."}},"subtopic":"...","question_type":"mcq","has_image":false,"image_description":null}}]"""

        pdf_part = types.Part.from_bytes(data=chapter_pdf_bytes, mime_type="application/pdf")
        raw = await self._call_gemini([pdf_part, prompt], timeout=120)
        questions = parse_llm_json(raw)
        return questions if isinstance(questions, list) else []

    async def _pass2_solve(self, questions: list[dict], batch_size: int = 5) -> list[dict]:
        """Pass 2: Solve extracted questions in batches (text only, no PDF)."""
        PASS2_PROMPT = """You are a math expert. Below is a JSON array of math questions from an Azerbaijani DIM exam.

For each question, solve it mathematically and return the correct answer and solution steps.

RULES:
- For MCQ (opts not null): solve the problem, identify which option letter (A/B/C/D/E) is the correct answer
- For open_ended (opts null): compute the exact numerical or expression answer
- solution_steps: step-by-step solution in Azerbaijani (2-5 key steps using LaTeX for math)
- correct_answer: letter A/B/C/D/E for MCQ, or computed answer text for open_ended
- For matching questions ("uyğunluğu müəyyən edin"): answer format "1-c; 2-a; 3-b,e"
- If you cannot solve (e.g. depends entirely on an image): set correct_answer to null

Return ONLY a valid JSON array with exactly one object per input, in the same order:
[{"i": 0, "correct_answer": "C", "solution_steps": "..."}]

QUESTIONS:
"""
        sol_map: dict = {}
        total = len(questions)
        for batch_start in range(0, total, batch_size):
            batch = questions[batch_start:batch_start + batch_size]
            batch_json = json.dumps(
                [{"i": batch_start + j, "q": q["question_text"], "opts": q.get("options")} for j, q in enumerate(batch)],
                ensure_ascii=False,
            )
            raw = await self._call_gemini([PASS2_PROMPT + batch_json], timeout=90)
            solutions = parse_llm_json(raw)
            if isinstance(solutions, list):
                for s in solutions:
                    if "i" in s:
                        sol_map[s["i"]] = s
            await asyncio.sleep(2)

        for i, q in enumerate(questions):
            sol = sol_map.get(i, {})
            q["correct_answer"] = sol.get("correct_answer")
            q["solution_steps"] = sol.get("solution_steps", "")
        return questions

    async def parse_chapter(
        self,
        chapter_pdf_bytes: bytes,
        chapter_name: str,
        subject: str,
    ) -> list[dict]:
        """
        Two-pass extraction:
        Pass 1 → extract ALL questions (max count, no solving)
        Pass 2 → solve all questions in one call (no PDF, text only)
        """
        print(f"      Pass 1: extracting questions...")
        questions = await self._pass1_extract(chapter_pdf_bytes, chapter_name)
        print(f"      Pass 1: {len(questions)} questions extracted")

        if not questions:
            return []

        # Proactive delay before Pass 2 — avoids back-to-back 503s
        await asyncio.sleep(5)

        print(f"      Pass 2: solving {len(questions)} questions...")
        questions = await self._pass2_solve(questions)

        for q in questions:
            q["id"] = str(uuid.uuid4())
            q["subject"] = subject
            q["topic"] = chapter_name
            q["year"] = 2025
            q["source_type"] = "dim_test"

            # difficulty_estimated default if missing
            if "difficulty_estimated" not in q:
                q["difficulty_estimated"] = "medium"

            # --- Post-processing quality checks ---
            needs_review = False

            # Image-based questions cannot be fully verified
            if q.get("has_image"):
                needs_review = True

            # No correct answer resolved
            if q.get("correct_answer") is None:
                needs_review = True

            # MCQ: answer must be a valid letter
            if q.get("question_type") == "mcq":
                if q.get("correct_answer") not in {"A", "B", "C", "D", "E"}:
                    needs_review = True

            # MCQ: duplicate or incomplete options
            if q.get("question_type") == "mcq" and q.get("options"):
                opts = q["options"]
                vals = list(opts.values())
                if set(opts.keys()) != {"A", "B", "C", "D", "E"} or len(set(vals)) < len(vals):
                    needs_review = True

            q["needs_review"] = needs_review

        return questions

    async def parse_all_chapters(
        self,
        pdf_path: str,
        subject: str,
        chapters: list[dict],
        answer_key_start: int,
        answer_key_end: int,
        cache_dir: Path,
        delay_seconds: float = 5.0,
    ) -> list[dict]:
        """
        Process each chapter with caching. Returns all questions combined.
        answer_key_start/end kept for API compatibility but no longer used.
        """
        cache_dir.mkdir(parents=True, exist_ok=True)

        all_questions: list[dict] = []
        total = len(chapters)

        for i, ch in enumerate(chapters, 1):
            cache_file = cache_dir / f"{ch['id']}.json"

            if cache_file.exists():
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                print(f"   [{i}/{total}] CACHE: {ch['name']} → {len(cached)} questions")
                all_questions.extend(cached)
                continue

            chapter_pages = ch["end"] - ch["start"]
            print(f"   [{i}/{total}] Processing: {ch['name']} ({chapter_pages} pages) ...")

            chapter_bytes = extract_pages_bytes(pdf_path, ch["start"], ch["end"])

            try:
                questions = await self.parse_chapter(
                    chapter_pdf_bytes=chapter_bytes,
                    chapter_name=ch["name"],
                    subject=subject,
                )
                print(f"      → {len(questions)} questions total")

                cache_file.write_text(
                    json.dumps(questions, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                all_questions.extend(questions)

            except Exception as e:
                print(f"      ERROR: {e}")

            if i < total:
                await asyncio.sleep(delay_seconds)

        return all_questions
