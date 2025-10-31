"""
Módulo responsável pelo gerenciamento do vector store (ChromaDB)
"""

import os
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from .config import Config


def get_persist_dir() -> str:
    """
    Retorna o diretório de persistência do ChromaDB

    Returns:
        Caminho do diretório
    """
    return Config.PERSIST_DIR


def load_existing_vector_store() -> Optional[Chroma]:
    """
    Carrega um vector store existente do disco

    Returns:
        Instância do Chroma se existir, None caso contrário
    """
    persist_directory = get_persist_dir()

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        try:
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=OpenAIEmbeddings(),
            )
            return vector_store
        except Exception as e:
            print(f"Erro ao carregar vector store: {e}")
            return None

    return None


def create_vector_store(chunks: List[Document]) -> Chroma:
    """
    Cria um novo vector store a partir de chunks de documentos

    Args:
        chunks: Lista de documentos

    Returns:
        Instância do Chroma
    """
    persist_directory = get_persist_dir()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory,
    )

    return vector_store


def add_to_vector_store(
    chunks: List[Document], vector_store: Optional[Chroma] = None
) -> Chroma:
    """
    Adiciona documentos a um vector store existente ou cria um novo

    Args:
        chunks: Lista de documentos para adicionar
        vector_store: Vector store existente (opcional)

    Returns:
        Instância do Chroma (existente ou novo)
    """
    if vector_store:
        # Adiciona ao vector store existente
        vector_store.add_documents(chunks)
        return vector_store
    else:
        # Cria um novo vector store
        return create_vector_store(chunks)


def delete_vector_store():
    """
    Remove completamente o vector store do disco
    """
    persist_directory = get_persist_dir()

    if os.path.exists(persist_directory):
        import shutil

        shutil.rmtree(persist_directory)
        print(f"Vector store removido: {persist_directory}")


def get_vector_store_stats(vector_store: Optional[Chroma]) -> dict:
    """
    Retorna estatísticas sobre o vector store

    Args:
        vector_store: Instância do Chroma

    Returns:
        Dicionário com estatísticas
    """
    if not vector_store:
        return {"exists": False, "total_documents": 0}

    try:
        # Tenta obter a coleção
        collection = vector_store._collection
        count = collection.count()

        return {
            "exists": True,
            "total_documents": count,
            "persist_directory": get_persist_dir(),
        }
    except Exception as e:
        return {"exists": True, "total_documents": "unknown", "error": str(e)}
