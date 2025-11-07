"""
Módulo responsável pelo processamento de arquivos (PDF, TXT, Markdown)
"""

import os
import re
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


def process_txt_file(file_like) -> List[Document]:
    """
    Processa um arquivo TXT e retorna chunks de documentos

    Args:
        file_like: Objeto file-like (ex: st.uploaded_file) que possui método .read()

    Returns:
        Lista de documentos (chunks) processados
    """
    # Lê o conteúdo do arquivo
    content = file_like.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    # Cria um documento único
    doc = Document(
        page_content=content, metadata={"source": file_like.name, "type": "txt"}
    )

    # Divide em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_documents([doc])
    return chunks


def process_markdown_file(file_like) -> List[Document]:
    """
    Processa um arquivo Markdown mantendo estrutura, extrai imagens/vídeos e retorna chunks.

    Args:
        file_like: Objeto file-like (ex: st.uploaded_file) que possui método .read()

    Returns:
        Lista de documentos (chunks) processados
    """
    # Lê o conteúdo do arquivo
    content = file_like.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    # Regex para encontrar imagens no formato ![alt-text](./images/filename.png "title")
    img_regex = r"!\[([^\]]*)\]\(./images/([^\"]+\.(?:png|jpg|jpeg|gif|webp))(?:\s+\"([^\"]*)\")?\)"
    
    # Regex para encontrar vídeos no formato ![alt-text](./videos/filename.mp4 "title")
    # Captura o nome completo do arquivo até .mp4, mesmo com parênteses no nome
    video_regex = r"!\[([^\]]*)\]\(./videos/([^\"]+\.mp4)(?:\s+\"([^\"]*)\")?\)"

    # Encontra todas as imagens e vídeos
    images_found = re.findall(img_regex, content)
    videos_found = re.findall(video_regex, content)
    
    # Substitui as sintaxes por tags que o frontend entende
    content_processed = re.sub(img_regex, r"[image: \2]", content)
    content_processed = re.sub(video_regex, r"[video: \2]", content_processed)

    # Divide o conteúdo em chunks primeiro
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""],
    )
    text_chunks = text_splitter.split_text(content_processed)

    # Cria um Document para cada chunk e associa os metadados corretos
    chunks = []
    for text_chunk in text_chunks:
        doc = Document(
            page_content=text_chunk,
            metadata={"source": file_like.name, "type": "markdown"},
        )
        chunks.append(doc)

    # Para cada chunk, verifica se ele contém tags de imagem/vídeo e adiciona os
    # nomes dos arquivos correspondentes aos seus metadados.
    for chunk in chunks:
        chunk_images = []
        chunk_videos = []
        
        # Procura por imagens
        for img_name in (img[1] for img in images_found):
            if f"[image: {img_name}]" in chunk.page_content:
                chunk_images.append(img_name)
        
        # Procura por vídeos
        for video_name in (video[1] for video in videos_found):
            if f"[video: {video_name}]" in chunk.page_content:
                chunk_videos.append(video_name)
        
        chunk.metadata["images"] = ",".join(chunk_images)
        chunk.metadata["videos"] = ",".join(chunk_videos)

    return chunks


def process_multiple_files(files) -> List[Document]:
    """
    Processa múltiplos arquivos (PDF, TXT, Markdown)

    Args:
        files: Lista de objetos file-like

    Returns:
        Lista combinada de todos os chunks processados
    """
    all_chunks = []

    for file in files:
        # Detecta a extensão do arquivo
        file_extension = file.name.split(".")[-1].lower()

        try:
            if file_extension == "pdf":
                chunks = process_pdf_file(file)
            elif file_extension == "txt":
                chunks = process_txt_file(file)
            elif file_extension in ["md", "markdown"]:
                chunks = process_markdown_file(file)
            else:
                # Ignora arquivos não suportados
                print(f"⚠️ Tipo de arquivo não suportado: {file.name}")
                continue

            all_chunks.extend(chunks)

        except Exception as e:
            print(f"❌ Erro ao processar {file.name}: {str(e)}")
            continue

    return all_chunks


def process_multiple_pdfs(files) -> List[Document]:
    """
    DEPRECATED: Use process_multiple_files() ao invés desta função.
    Mantida para compatibilidade com código existente.

    Processa múltiplos arquivos PDF

    Args:
        files: Lista de objetos file-like

    Returns:
        Lista combinada de todos os chunks processados
    """
    return process_multiple_files(files)


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
