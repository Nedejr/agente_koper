"""
Módulo responsável pelo gerenciamento do vector store (ChromaDB)
"""

import os
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from .config import Config


def _ensure_directory_permissions(directory: str):
    """
    Garante que o diretório e seus arquivos tenham permissões adequadas

    Args:
        directory: Caminho do diretório
    """
    try:
        import stat

        # Define permissões de leitura/escrita para o usuário
        if os.path.exists(directory):
            # Permissões para o diretório: rwxr-xr-x (0o755)
            os.chmod(
                directory,
                stat.S_IRWXU
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH,
            )

            # Permissões para todos os arquivos dentro: rw-r--r-- (0o644)
            for root, dirs, files in os.walk(directory):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    os.chmod(
                        dir_path,
                        stat.S_IRWXU
                        | stat.S_IRGRP
                        | stat.S_IXGRP
                        | stat.S_IROTH
                        | stat.S_IXOTH,
                    )
                for f in files:
                    file_path = os.path.join(root, f)
                    os.chmod(
                        file_path,
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
                    )
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível ajustar permissões: {e}")


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
            # Verifica e corrige permissões do diretório
            _ensure_directory_permissions(persist_directory)

            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=OpenAIEmbeddings(),
            )

            # Tenta fazer uma operação de leitura para validar o banco
            try:
                vector_store._collection.count()
            except Exception as count_error:
                print(f"⚠️ Banco de dados corrompido ou readonly: {count_error}")
                print("🔄 Removendo banco corrompido...")
                delete_vector_store()
                return None

            return vector_store
        except Exception as e:
            print(f"❌ Erro ao carregar vector store: {e}")
            # Se houver erro, tenta limpar o banco corrompido
            try:
                print("🔄 Tentando remover banco corrompido...")
                delete_vector_store()
            except Exception as cleanup_error:
                print(f"⚠️ Erro ao limpar banco: {cleanup_error}")
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

    # Garante que o diretório existe com permissões corretas
    os.makedirs(persist_directory, exist_ok=True)
    _ensure_directory_permissions(persist_directory)

    try:
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=OpenAIEmbeddings(),
            persist_directory=persist_directory,
        )

        # Verifica se o banco foi criado corretamente
        vector_store._collection.count()

        return vector_store
    except Exception as e:
        print(f"❌ Erro ao criar vector store: {e}")
        # Tenta limpar se houver erro
        try:
            delete_vector_store()
        except Exception:
            pass
        raise


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
        try:
            # Adiciona ao vector store existente
            vector_store.add_documents(chunks)

            # Verifica se a adição foi bem-sucedida
            vector_store._collection.count()

            return vector_store
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos ao vector store: {e}")
            print("🔄 Tentando recriar o vector store...")

            # Se falhar, tenta recriar o vector store
            try:
                delete_vector_store()
                return create_vector_store(chunks)
            except Exception as recreate_error:
                print(f"❌ Erro ao recriar vector store: {recreate_error}")
                raise
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

        try:
            shutil.rmtree(persist_directory)
            print(f"✅ Vector store removido: {persist_directory}")
        except Exception as e:
            print(f"❌ Erro ao remover vector store: {e}")
            raise


def check_and_repair_vector_store() -> Optional[Chroma]:
    """
    Verifica a integridade do vector store e tenta repará-lo se necessário

    Returns:
        Instância do Chroma se válida, None caso contrário
    """
    persist_directory = get_persist_dir()

    if not os.path.exists(persist_directory):
        return None

    try:
        # Tenta carregar o vector store
        vector_store = load_existing_vector_store()

        if vector_store:
            # Tenta uma operação de leitura para validar
            count = vector_store._collection.count()
            print(f"✅ Vector store válido com {count} documentos")
            return vector_store
        else:
            return None

    except Exception as e:
        print(f"❌ Vector store corrompido: {e}")
        print("🔄 Removendo banco corrompido...")
        try:
            delete_vector_store()
        except Exception:
            pass
        return None


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
