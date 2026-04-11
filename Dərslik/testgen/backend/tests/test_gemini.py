import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_gemini_generate_text():
    from core.gemini_client import GeminiClient

    mock_response = MagicMock()
    mock_response.text = '{"question": "test?"}'

    with patch("core.gemini_client.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        client = GeminiClient(api_key="fake-key")
        result = await client.generate("Test prompt")
        assert result == '{"question": "test?"}'


@pytest.mark.asyncio
async def test_gemini_generate_json():
    from core.gemini_client import GeminiClient

    mock_response = MagicMock()
    mock_response.text = '{"question": "What is 2+2?", "answer": "4"}'

    with patch("core.gemini_client.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        client = GeminiClient(api_key="fake-key")
        result = await client.generate_json("Generate a math question")
        assert '"question"' in result
        assert '"answer"' in result


@pytest.mark.asyncio
async def test_gemini_embed_text():
    from core.embedding import EmbeddingClient

    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 3072)]

    with patch("core.embedding.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)

        client = EmbeddingClient(api_key="fake-key")
        result = await client.embed("Test text")
        assert len(result) == 3072


@pytest.mark.asyncio
async def test_gemini_embed_batch():
    from core.embedding import EmbeddingClient

    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.1] * 3072)]

    with patch("core.embedding.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)

        client = EmbeddingClient(api_key="fake-key")
        results = await client.embed_batch(["Text 1", "Text 2"])
        assert len(results) == 2
        assert len(results[0]) == 3072