"""
Módulo responsável pelo processamento de arquivos PDF
"""

import os
import tempfile
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import Config


def process_pdf_file(file_like) -> List[Document]:
    """
    Processa um arquivo PDF e retorna chunks de documentos

    Args:
        file_like: Objeto file-like (ex: st.uploaded_file) que possui método .read()

    Returns:
        Lista de documentos (chunks) processados
    """
    # Cria arquivo temporário para salvar o PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_like.read())
        tmp_path = tmp.name

    try:
        # Carrega o PDF
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        # Divide em chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documents=docs)

        return chunks

    finally:
        # Remove o arquivo temporário
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def process_multiple_pdfs(files) -> List[Document]:
    """
    Processa múltiplos arquivos PDF

    Args:
        files: Lista de objetos file-like

    Returns:
        Lista combinada de todos os chunks processados
    """
    all_chunks = []

    for file in files:
        chunks = process_pdf_file(file)
        all_chunks.extend(chunks)

    return all_chunks


def get_document_stats(chunks: List[Document]) -> dict:
    """
    Retorna estatísticas sobre os documentos processados

    Args:
        chunks: Lista de documentos

    Returns:
        Dicionário com estatísticas
    """
    total_chars = sum(len(doc.page_content) for doc in chunks)

    return {
        "total_chunks": len(chunks),
        "total_characters": total_chars,
        "avg_chunk_size": total_chars // len(chunks) if chunks else 0,
    }
