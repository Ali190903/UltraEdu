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

from core.embedding import EmbeddingClient
from core.qdrant_client import QdrantWrapper
from data_pipeline.pdf_processor import PdfProcessor
from data_pipeline.toc_extractor import TocExtractor
from data_pipeline.chunker import Chunker
from data_pipeline.dim_parser import (
    DimParser,
    DIM_RIYAZIYYAT_1_CHAPTERS,
    ANSWER_KEY_START,
    ANSWER_KEY_END,
)
from data_pipeline.indexer import Indexer

SUBJECT_MAP = {
    "az_dili": "Azerbaycan_dili_tedris.pdf",
    "riyaziyyat": "Riyaziyyat.pdf",
    "ingilis": {"sinif9": "ingilis_dili.pdf", "sinif10": "ingili-dili.pdf", "sinif11": "ing_dili.pdf"},
}

GRADE_DIRS = {9: "sinif9", 10: "sinif10", 11: "sinif11"}


from data_pipeline.topic_extractor import extract_mini_pdf, TopicExtractor

async def process_textbook(
    pdf_path: str,
    subject: str,
    grade: int,
    embedding: EmbeddingClient,
    qdrant: QdrantWrapper,
    offset: int = 2,
):
    print(f"\n--- Processing textbook: {subject} grade {grade} ---")
    print(f"PDF: {pdf_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    toc_extractor = TocExtractor(api_key=api_key)
    topic_extractor = TopicExtractor(api_key=api_key)
    chunker = Chunker(max_tokens=1000)
    indexer = Indexer(embedding=embedding, qdrant=qdrant)

    # --- Cache directories ---
    cache_dir = Path(__file__).resolve().parent.parent / ".pipeline_cache"
    cache_dir.mkdir(exist_ok=True)
    toc_cache = cache_dir / f"{subject}_{grade}_toc.json"
    
    topics_cache_dir = cache_dir / "topics"
    topics_cache_dir.mkdir(exist_ok=True)

    # --- 1. TOC ---
    if toc_cache.exists():
        print("1. Loading cached TOC...")
        toc = json.loads(toc_cache.read_text(encoding="utf-8"))
    else:
        print("1. Extracting TOC...")
        toc = await toc_extractor.extract(pdf_path)
        toc_cache.write_text(json.dumps(toc, ensure_ascii=False, indent=2), encoding="utf-8")
    
    total_topics = sum(len(ch['topics']) for ch in toc)
    print(f"   Found {total_topics} topics in {len(toc)} chapters")

    # --- 2. Extract strictly by Topic & Chunk ---
    print("2. Extracting text topic-by-topic & Chunking...")
    all_chunks = []
    topic_counter = 0
    
    for chapter in toc:
        chapter_name = chapter["chapter"]
        for topic_info in chapter["topics"]:
            topic_counter += 1
            topic_name = topic_info["topic"]
            subtopic = topic_info.get("subtopic")
            
            book_start = topic_info.get("page_start")
            book_end = topic_info.get("page_end")
            
            if not book_start or not book_end:
                print(f"   [{topic_counter}/{total_topics}] SKIP: {topic_name} (Missing page range)")
                continue
                
            pdf_start = book_start + offset
            pdf_end = book_end + offset
            
            pages_str = f"{book_start}-{book_end}"
            
            topic_cache_file = topics_cache_dir / f"{subject}_{grade}_topic_{topic_counter:03d}.json"
            
            if topic_cache_file.exists():
                print(f"   [{topic_counter}/{total_topics}] Load cached: {topic_name[:40]}...")
                extracted_data = json.loads(topic_cache_file.read_text(encoding="utf-8"))
            else:
                print(f"   [{topic_counter}/{total_topics}] Extracting: {topic_name[:40]} (Pages {pages_str})...")
                # Free PyMuPDF slice
                pdf_bytes = extract_mini_pdf(pdf_path, pdf_start, pdf_end)
                
                # Sleep a bit to respect Gemini Rate Limits
                if topic_counter > 1:
                    await asyncio.sleep(4)
                    
                # Gemini Mini-PDF call
                extracted_data = await topic_extractor.extract_topic(pdf_bytes, topic_name)
                
                # Save cache
                topic_cache_file.write_text(json.dumps(extracted_data, ensure_ascii=False, indent=2), encoding="utf-8")

            if isinstance(extracted_data, list):
                extracted_data = extracted_data[0] if extracted_data else {}

            # Chunk the topic
            topic_chunks = chunker.chunk_topic(
                extracted_data=extracted_data,
                chapter=chapter_name,
                subject=subject,
                grade=grade,
                pages=pages_str,
                subtopic=subtopic
            )
            all_chunks.extend(topic_chunks)

    print(f"   Created total {len(all_chunks)} chunks from {total_topics} topics")

    print("3. Embedding & indexing into Qdrant...")
    await indexer.index_textbook_chunks(all_chunks)
    print(f"   Done! {qdrant.count('textbooks')} total chunks in textbooks collection")

    return toc


async def process_dim_tests(
    pdf_path: str,
    subject: str,
    embedding: EmbeddingClient,
    qdrant: QdrantWrapper,
    cache_key: str = "dim",
):
    print(f"\n--- Processing DIM tests: {subject} ---")
    print(f"PDF: {pdf_path}")

    api_key = os.getenv("GEMINI_API_KEY")
    parser = DimParser(api_key=api_key)
    indexer = Indexer(embedding=embedding, qdrant=qdrant)

    cache_dir = Path(__file__).resolve().parent.parent / ".pipeline_cache" / cache_key
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Determine chapter map based on subject + cache_key
    if subject == "riyaziyyat" and "riyaziyyat_1" in cache_key:
        chapters = DIM_RIYAZIYYAT_1_CHAPTERS
        ans_start = ANSWER_KEY_START
        ans_end = ANSWER_KEY_END
    else:
        chapters = DIM_RIYAZIYYAT_1_CHAPTERS
        ans_start = ANSWER_KEY_START
        ans_end = ANSWER_KEY_END

    print(f"1. Extracting questions chapter-by-chapter ({len(chapters)} chapters) ...")
    questions = await parser.parse_all_chapters(
        pdf_path=pdf_path,
        subject=subject,
        chapters=chapters,
        answer_key_start=ans_start,
        answer_key_end=ans_end,
        cache_dir=cache_dir,
        delay_seconds=5.0,
    )
    print(f"   Total extracted: {len(questions)} questions")

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
    parser.add_argument("--cache-key", type=str, default="dim",
                        help="Cache subfolder name, e.g. dim_riyaziyyat_1 or dim_riyaziyyat_2")
    parser.add_argument("--qdrant-url", type=str, default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    embedding = EmbeddingClient(api_key=api_key)
    qdrant = QdrantWrapper(url=args.qdrant_url)
    qdrant.ensure_collections()

    if args.mode == "textbooks" and args.pdf_path:
        toc = await process_textbook(args.pdf_path, args.subject, args.grade, embedding, qdrant)
        await save_topics_to_db(toc, args.subject, args.grade)

    elif args.mode == "dim" and args.pdf_path:
        await process_dim_tests(args.pdf_path, args.subject, embedding, qdrant, cache_key=args.cache_key)

    elif args.mode == "all":
        base_dir = Path(__file__).resolve().parent.parent.parent
        for grade, grade_dir in GRADE_DIRS.items():
            for subject in ["az_dili", "riyaziyyat", "ingilis"]:
                filename = SUBJECT_MAP[subject]
                if isinstance(filename, dict):
                    filename = filename[grade_dir]
                pdf_path = base_dir / grade_dir / filename
                if pdf_path.exists():
                    toc = await process_textbook(str(pdf_path), subject, grade, embedding, qdrant)
                    await save_topics_to_db(toc, subject, grade)
                else:
                    print(f"SKIP: {pdf_path} not found")

    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    asyncio.run(main())