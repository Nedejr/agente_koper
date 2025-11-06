#!/usr/bin/env python3
"""
Script de teste para processamento de imagens
Testa o fluxo completo: processamento → indexação → busca
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.rag.document_processor import document_processor
from backend.utils.logger import log


def test_image_processing():
    """
    Testa o processamento de um arquivo markdown com imagens
    """
    log.info("=" * 60)
    log.info("🧪 Testando processamento de imagens")
    log.info("=" * 60)
    
    # Caminho para o arquivo de teste
    test_file = project_root / "docs" / "gestao-epi" / "gestao-epi.md"
    
    if not test_file.exists():
        log.error(f"❌ Arquivo de teste não encontrado: {test_file}")
        return False
    
    try:
        # Processa o arquivo
        log.info(f"📝 Processando: {test_file}")
        
        chunks = document_processor.process_text(
            file_path=str(test_file),
            metadata={"section": "gestao-epi"},
            file_type="md",
            process_images=True
        )
        
        # Estatísticas
        total_chunks = len(chunks)
        chunks_with_images = sum(1 for c in chunks if c.metadata.get("images"))
        total_images = sum(len(c.metadata.get("images", [])) for c in chunks)
        
        log.info("=" * 60)
        log.info("📊 Resultados:")
        log.info(f"   Total de chunks: {total_chunks}")
        log.info(f"   Chunks com imagens: {chunks_with_images}")
        log.info(f"   Total de imagens: {total_images}")
        log.info("=" * 60)
        
        # Mostra alguns exemplos
        log.info("\n📸 Exemplos de chunks com imagens:")
        
        count = 0
        for i, chunk in enumerate(chunks):
            images = chunk.metadata.get("images", [])
            if images and count < 3:  # Mostra até 3 exemplos
                log.info(f"\n--- Chunk {i} ---")
                log.info(f"Conteúdo (primeiros 100 chars): {chunk.page_content[:100]}...")
                log.info(f"Imagens associadas:")
                for img in images:
                    log.info(f"  • {img['filename']}")
                    log.info(f"    Seção: {img['section']}")
                    log.info(f"    Legenda: {img['caption'][:80]}...")
                count += 1
        
        # Verifica se encontrou imagens
        if chunks_with_images == 0:
            log.warning("⚠️  Nenhuma imagem foi associada aos chunks!")
            log.warning("   Verifique o images-map.json")
            return False
        
        log.info("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        log.error(f"❌ Erro no teste: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_image_processing()
    sys.exit(0 if success else 1)

