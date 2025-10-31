#!/usr/bin/env python
"""
Script de teste para verificar o processamento de diferentes tipos de arquivo
"""

import sys
from io import BytesIO

sys.path.insert(0, ".")

from backend.processing import (
    get_document_stats,
    process_markdown_file,
    process_multiple_files,
    process_pdf_file,
    process_txt_file,
)


def test_txt_processing():
    """Testa processamento de arquivo TXT"""
    print("🧪 Testando processamento de TXT...")

    content = b"""Sistema de Gestao Empresarial

MODULO DE VENDAS
================

Funcionalidades:
- Cadastro de clientes
- Registro de pedidos
- Emissao de notas fiscais
- Controle de estoque
- Relatorios de vendas

Para mais informacoes, consulte o manual do usuario.
"""

    file_obj = BytesIO(content)
    file_obj.name = "teste.txt"

    chunks = process_txt_file(file_obj)
    stats = get_document_stats(chunks)

    print(f"  ✅ Arquivo TXT processado com sucesso!")
    print(f"  📊 Total de chunks: {stats['total_chunks']}")
    print(f"  📝 Total de caracteres: {stats['total_characters']}")
    print(f"  📏 Tamanho médio do chunk: {stats['avg_chunk_size']}\n")

    return chunks


def test_markdown_processing():
    """Testa processamento de arquivo Markdown"""
    print("🧪 Testando processamento de Markdown...")

    content = b"""# API REST - Sistema de Vendas

## Autenticacao

Todos os endpoints requerem autenticacao via token JWT.

### Login
```http
POST /api/auth/login
Content-Type: application/json
```

## Endpoints Principais

### 1. Listar Produtos

```http
GET /api/products
Authorization: Bearer {token}
```

**Query Parameters:**
- `category` (opcional): Filtrar por categoria
- `search` (opcional): Buscar por nome

### 2. Criar Pedido

```http
POST /api/orders
Authorization: Bearer {token}
```

## Codigos de Status

| Codigo | Descricao |
|--------|-----------|
| 200 | Sucesso |
| 401 | Nao autenticado |
| 404 | Nao encontrado |
"""

    file_obj = BytesIO(content)
    file_obj.name = "teste.md"

    chunks = process_markdown_file(file_obj)
    stats = get_document_stats(chunks)

    print(f"  ✅ Arquivo Markdown processado com sucesso!")
    print(f"  📊 Total de chunks: {stats['total_chunks']}")
    print(f"  📝 Total de caracteres: {stats['total_characters']}")
    print(f"  📏 Tamanho médio do chunk: {stats['avg_chunk_size']}\n")

    return chunks


def test_multiple_files():
    """Testa processamento de múltiplos arquivos de tipos diferentes"""
    print("🧪 Testando processamento de múltiplos arquivos...")

    # Cria arquivo TXT
    txt_content = b"Documento TXT de teste.\n\nConteudo simples."
    txt_file = BytesIO(txt_content)
    txt_file.name = "doc1.txt"

    # Cria arquivo Markdown
    md_content = b"# Documento MD\n\n## Secao 1\nConteudo markdown."
    md_file = BytesIO(md_content)
    md_file.name = "doc2.md"

    # Processa múltiplos arquivos
    files = [txt_file, md_file]
    all_chunks = process_multiple_files(files)
    stats = get_document_stats(all_chunks)

    print(f"  ✅ {len(files)} arquivos processados com sucesso!")
    print(f"  📊 Total de chunks: {stats['total_chunks']}")
    print(f"  📝 Total de caracteres: {stats['total_characters']}\n")

    return all_chunks


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("🚀 TESTES DE PROCESSAMENTO DE DOCUMENTOS")
    print("=" * 60 + "\n")

    try:
        # Testa cada tipo de arquivo
        txt_chunks = test_txt_processing()
        md_chunks = test_markdown_processing()
        multiple_chunks = test_multiple_files()

        # Resumo
        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 60)
        print(f"\nResumo:")
        print(f"  📄 TXT chunks: {len(txt_chunks)}")
        print(f"  📝 Markdown chunks: {len(md_chunks)}")
        print(f"  📦 Múltiplos arquivos chunks: {len(multiple_chunks)}")
        print(f"  🎯 Total geral: {len(txt_chunks) + len(md_chunks) + len(multiple_chunks)}")
        print("\n✨ Sistema pronto para uso!\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
