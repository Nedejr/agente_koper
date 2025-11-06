#!/usr/bin/env python3
"""
Script para indexar documentação da pasta docs/
Processa arquivos markdown com imagens e adiciona ao vector store
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings
from backend.rag.document_processor import document_processor
from backend.rag.indexer import indexer
from backend.utils.logger import log


def find_markdown_files(docs_dir: Path) -> list:
    """
    Encontra todos os arquivos markdown na pasta docs
    
    Args:
        docs_dir: Diretório docs
        
    Returns:
        Lista de caminhos para arquivos markdown
    """
    markdown_files = []
    
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(Path(root) / file)
    
    return markdown_files


async def index_documentation():
    """
    Indexa toda a documentação da pasta docs/
    """
    log.info("=" * 60)
    log.info("📚 Iniciando indexação da documentação")
    log.info("=" * 60)
    
    # Encontra pasta docs (verifica se está no Docker ou local)
    if os.path.exists("/app/docs"):
        docs_dir = Path("/app/docs")
        log.info("🐳 Rodando no Docker")
    else:
        docs_dir = project_root / "docs"
        log.info("💻 Rodando localmente")
    
    if not docs_dir.exists():
        log.error(f"❌ Pasta docs não encontrada: {docs_dir}")
        return
    
    log.info(f"📁 Buscando documentos em: {docs_dir}")
    
    # Encontra arquivos markdown
    markdown_files = find_markdown_files(docs_dir)
    
    if not markdown_files:
        log.warning("⚠️  Nenhum arquivo markdown encontrado")
        return
    
    log.info(f"✅ Encontrados {len(markdown_files)} arquivos markdown")
    
    # Processa cada arquivo
    total_chunks = 0
    
    for md_file in markdown_files:
        try:
            log.info(f"📝 Processando: {md_file.relative_to(project_root)}")
            
            # Metadata adicional
            metadata = {
                "section": md_file.parent.name,
                "filename": md_file.name,
                "full_path": str(md_file),
            }
            
            # Processa documento (com imagens se disponível)
            chunks = document_processor.process_text(
                file_path=str(md_file),
                metadata=metadata,
                file_type="md",
                process_images=True
            )
            
            if not chunks:
                log.warning(f"⚠️  Nenhum chunk gerado para {md_file.name}")
                continue
            
            # Conta chunks com imagens
            chunks_with_images = sum(
                1 for c in chunks 
                if c.metadata.get("images")
            )
            total_images = sum(
                len(c.metadata.get("images", [])) 
                for c in chunks
            )
            
            log.info(
                f"   ✓ {len(chunks)} chunks criados "
                f"({chunks_with_images} com imagens, {total_images} imagens no total)"
            )
            
            # Indexa no vector store
            await indexer.index_documents(
                documents=chunks,
                collection_name=settings.qdrant_collection_name
            )
            
            total_chunks += len(chunks)
            
            log.info(f"   ✓ Indexado com sucesso")
            
        except Exception as e:
            log.error(f"❌ Erro processando {md_file.name}: {str(e)}")
            continue
    
    log.info("=" * 60)
    log.info(f"✅ Indexação concluída!")
    log.info(f"📊 Total de chunks indexados: {total_chunks}")
    log.info(f"📚 Collection: {settings.qdrant_collection_name}")
    log.info("=" * 60)


if __name__ == "__main__":
    import asyncio
    
    # Executa indexação
    asyncio.run(index_documentation())

