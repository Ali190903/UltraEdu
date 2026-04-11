from unittest.mock import MagicMock, patch


def test_qdrant_wrapper_search():
    from core.qdrant_client import QdrantWrapper

    mock_client = MagicMock()
    mock_hit = MagicMock()
    mock_hit.payload = {"text_content": "sample chunk", "subject": "math"}
    mock_hit.score = 0.92
    mock_client.query_points.return_value.points = [mock_hit]

    with patch("core.qdrant_client.QdrantClient", return_value=mock_client):
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
    from core.qdrant_client import QdrantWrapper

    mock_client = MagicMock()

    with patch("core.qdrant_client.QdrantClient", return_value=mock_client):
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


def test_qdrant_wrapper_ensure_collections():
    from core.qdrant_client import QdrantWrapper

    mock_client = MagicMock()
    mock_client.get_collections.return_value.collections = []

    with patch("core.qdrant_client.QdrantClient", return_value=mock_client):
        wrapper = QdrantWrapper(url="http://fake:6333")
        wrapper.ensure_collections()
        assert mock_client.create_collection.call_count == 2


def test_qdrant_wrapper_count():
    from core.qdrant_client import QdrantWrapper

    mock_client = MagicMock()
    mock_client.count.return_value.count = 42

    with patch("core.qdrant_client.QdrantClient", return_value=mock_client):
        wrapper = QdrantWrapper(url="http://fake:6333")
        assert wrapper.count("textbooks") == 42