"""
Testes para o módulo de vector store
Execute: pytest tests/
"""

from unittest.mock import Mock

from backend.vector_store import get_persist_dir, get_vector_store_stats


def test_get_persist_dir():
    """Testa obtenção do diretório de persistência"""
    persist_dir = get_persist_dir()
    assert isinstance(persist_dir, str)
    assert len(persist_dir) > 0


def test_get_persist_dir_from_config():
    """Testa se usa Config.PERSIST_DIR"""
    from backend.config import Config

    persist_dir = get_persist_dir()
    assert persist_dir == Config.PERSIST_DIR


def test_get_vector_store_stats_none():
    """Testa estatísticas com vector store None"""
    stats = get_vector_store_stats(None)

    assert not stats["exists"]
    assert stats["total_documents"] == 0


def test_get_vector_store_stats_with_store():
    """Testa estatísticas com vector store mockado"""
    mock_store = Mock()
    mock_collection = Mock()
    mock_collection.count.return_value = 42
    mock_store._collection = mock_collection

    stats = get_vector_store_stats(mock_store)

    assert stats["exists"]
    assert stats["total_documents"] == 42
    assert "persist_directory" in stats


def test_get_vector_store_stats_handles_error():
    """Testa tratamento de erro ao obter estatísticas"""
    mock_store = Mock()
    mock_store._collection.count.side_effect = Exception("Test error")

    stats = get_vector_store_stats(mock_store)

    assert stats["exists"]
    assert stats["total_documents"] == "unknown"
    assert "error" in stats


# Nota: Testes de load_existing_vector_store, create_vector_store, etc.
# requerem setup de ChromaDB de teste ou heavy mocking
