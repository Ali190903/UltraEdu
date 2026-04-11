import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path


@pytest.mark.asyncio
async def test_pdf_processor_extracts_text():
    from data_pipeline.pdf_processor import PdfProcessor

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '[{"page": 1, "text": "Algebra basics", "has_image": false, "image_description": null, "latex": null}]'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("data_pipeline.pdf_processor.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        processor = PdfProcessor(api_key="fake")

        # Patch Path.exists and Path.read_bytes for a small file
        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "read_bytes", return_value=b"fake-pdf-bytes"):
            result = await processor.extract_text("fake/path.pdf", pages=(1, 5))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["page"] == 1
    assert result[0]["text"] == "Algebra basics"


@pytest.mark.asyncio
async def test_pdf_processor_file_not_found():
    from data_pipeline.pdf_processor import PdfProcessor

    with patch("data_pipeline.pdf_processor.genai") as mock_genai:
        mock_genai.Client.return_value = MagicMock()
        processor = PdfProcessor(api_key="fake")

        with pytest.raises(FileNotFoundError):
            await processor.extract_text("nonexistent/path.pdf")


@pytest.mark.asyncio
async def test_pdf_processor_uploads_large_file():
    """Files >50MB should use Files API upload."""
    from data_pipeline.pdf_processor import PdfProcessor, INLINE_PDF_LIMIT

    mock_client = MagicMock()
    mock_uploaded = MagicMock()
    mock_client.aio.files.upload = AsyncMock(return_value=mock_uploaded)

    mock_response = MagicMock()
    mock_response.text = '[{"page": 1, "text": "Large PDF content"}]'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    large_bytes = b"x" * (INLINE_PDF_LIMIT + 1)

    with patch("data_pipeline.pdf_processor.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        processor = PdfProcessor(api_key="fake")

        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "read_bytes", return_value=large_bytes):
            result = await processor.extract_text("big/file.pdf")

    mock_client.aio.files.upload.assert_called_once()
    assert isinstance(result, list)


def test_pdf_processor_page_count_estimate():
    from data_pipeline.pdf_processor import PdfProcessor

    with patch("data_pipeline.pdf_processor.genai"):
        processor = PdfProcessor(api_key="fake")

        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 500_000  # 500KB
            count = processor.get_page_count_estimate("some/file.pdf")
            assert count == 10  # 500000 // 50000

            mock_stat.return_value.st_size = 1000  # very small
            count = processor.get_page_count_estimate("tiny/file.pdf")
            assert count == 1  # min 1


@pytest.mark.asyncio
async def test_toc_extractor():
    from data_pipeline.toc_extractor import TocExtractor

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '[{"chapter": "Cəbr", "chapter_order": 1, "topics": [{"topic": "Tənliklər", "subtopic": null, "page_start": 5, "page_end": 20}]}]'
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("data_pipeline.toc_extractor.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        extractor = TocExtractor(api_key="fake")

        with patch.object(Path, "exists", return_value=True), \
             patch.object(Path, "read_bytes", return_value=b"fake-pdf-bytes"):
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
        "image_description": None,
    }])

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = sample_response
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("data_pipeline.dim_parser.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        parser = DimParser(api_key="fake")

        with patch.object(Path, "read_bytes", return_value=b"fake-pdf-bytes"):
            questions = await parser.parse("fake/dim_test.pdf", subject="az_dili")

    assert len(questions) == 1
    assert questions[0]["correct_answer"] == "A"
    assert questions[0]["subject"] == "az_dili"
    assert questions[0]["question_type"] == "mcq"
    assert "id" in questions[0]


@pytest.mark.asyncio
async def test_indexer_indexes_chunks():
    from data_pipeline.indexer import Indexer

    mock_embedding = MagicMock()
    mock_embedding.embed_batch = AsyncMock(return_value=[[0.1] * 3072])

    mock_qdrant = MagicMock()

    indexer = Indexer(embedding=mock_embedding, qdrant=mock_qdrant)

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


@pytest.mark.asyncio
async def test_indexer_indexes_dim_questions():
    from data_pipeline.indexer import Indexer

    mock_embedding = MagicMock()
    mock_embedding.embed_batch = AsyncMock(return_value=[[0.1] * 3072])

    mock_qdrant = MagicMock()

    indexer = Indexer(embedding=mock_embedding, qdrant=mock_qdrant)

    questions = [{
        "id": "q-123",
        "subject": "az_dili",
        "question_text": "Hansı söz düzgün yazılıb?",
        "options": {"A": "kitab", "B": "kitap"},
        "correct_answer": "A",
        "topic": "Orfoqrafiya",
        "difficulty_estimated": "easy",
        "question_type": "mcq",
        "year": 2024,
        "source_type": "dim_test",
        "has_image": False,
    }]

    await indexer.index_dim_questions(questions)
    mock_qdrant.upsert.assert_called_once()
    call_args = mock_qdrant.upsert.call_args
    assert call_args[1]["collection"] == "dim_tests"
    assert len(call_args[1]["points"]) == 1