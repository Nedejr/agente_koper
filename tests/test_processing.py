"""
Testes para o módulo de processamento de PDFs
Execute: pytest tests/
"""

from unittest.mock import Mock

import pytest

from backend.processing import (
    get_document_stats,
)


@pytest.fixture
def mock_pdf_file():
    """Cria um mock de arquivo PDF"""
    mock_file = Mock()
    mock_file.read.return_value = b"Mock PDF content"
    return mock_file


@pytest.fixture
def mock_document():
    """Cria um mock de documento LangChain"""
    mock_doc = Mock()
    mock_doc.page_content = "Este é um conteúdo de teste do documento."
    return mock_doc


def test_get_document_stats_empty():
    """Testa estatísticas com lista vazia"""
    stats = get_document_stats([])

    assert stats["total_chunks"] == 0
    assert stats["total_characters"] == 0
    assert stats["avg_chunk_size"] == 0


def test_get_document_stats_with_docs(mock_document):
    """Testa estatísticas com documentos"""
    docs = [mock_document, mock_document]
    stats = get_document_stats(docs)

    assert stats["total_chunks"] == 2
    assert stats["total_characters"] > 0
    assert stats["avg_chunk_size"] > 0


def test_get_document_stats_calculates_correctly():
    """Testa cálculo correto das estatísticas"""
    mock_doc1 = Mock()
    mock_doc1.page_content = "a" * 100  # 100 caracteres

    mock_doc2 = Mock()
    mock_doc2.page_content = "b" * 200  # 200 caracteres

    stats = get_document_stats([mock_doc1, mock_doc2])

    assert stats["total_chunks"] == 2
    assert stats["total_characters"] == 300
    assert stats["avg_chunk_size"] == 150


# Nota: Testes completos de process_pdf_file e process_multiple_pdfs
# requerem mocking mais complexo do PyPDFLoader e RecursiveCharacterTextSplitter
# ou uso de arquivos PDF de teste reais
