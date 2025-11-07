import os
import sys
from io import BytesIO

import pytest

# Adiciona o diretório raiz ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.processing import process_markdown_file
from backend.qa import ask_question
from backend.vector_store import create_vector_store


@pytest.fixture(scope="module")
def vector_store_with_docs():
    """Fixture para criar um vector store com o documento de EPI."""
    doc_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs-gestao-epi",
        "gestao_epi_documentacao.md",
    )

    if not os.path.exists(doc_path):
        pytest.fail("Documento de teste 'gestao_epi_documentacao.md' não encontrado.")

    with open(doc_path, "rb") as f:
        file_like = BytesIO(f.read())
        file_like.name = os.path.basename(doc_path)
        chunks = process_markdown_file(file_like)

    # Cria um vector store em memória para o teste
    vector_store = create_vector_store(chunks)
    return vector_store


def test_ask_question_about_epi_delivery_includes_image_tag(vector_store_with_docs):
    """
    Testa se ao perguntar sobre "entrega de EPI", a resposta do RAG
    retorna um documento fonte que contém a tag da imagem relevante.
    """
    query = "Como fazer uma entrega de EPI?"
    result = ask_question(query=query, vector_store=vector_store_with_docs)

    assert "answer" in result
    assert "source_documents" in result

    # Verifica se algum dos documentos fonte contém a tag da imagem esperada
    image_tag = "[image: modal-entrega-de-epi.png]"
    found_tag = any(image_tag in doc.page_content for doc in result["source_documents"])

    assert found_tag, f"A tag '{image_tag}' não foi encontrada nos documentos de origem."