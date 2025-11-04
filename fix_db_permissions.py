#!/usr/bin/env python3
"""
Script utilitário para diagnosticar e corrigir problemas com o ChromaDB
"""

import os
import sys
import stat

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.vector_store import (
    get_persist_dir,
    check_and_repair_vector_store,
    delete_vector_store,
    _ensure_directory_permissions,
)


def print_header(text: str):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_directory_permissions(directory: str):
    """Verifica as permissões de um diretório"""
    if not os.path.exists(directory):
        print(f"❌ Diretório não existe: {directory}")
        return False

    try:
        # Verifica permissões
        st = os.stat(directory)
        permissions = stat.filemode(st.st_mode)

        print(f"📁 Diretório: {directory}")
        print(f"   Permissões: {permissions}")
        print(f"   Owner UID: {st.st_uid}")
        print(f"   Owner GID: {st.st_gid}")

        # Verifica se pode ler e escrever
        can_read = os.access(directory, os.R_OK)
        can_write = os.access(directory, os.W_OK)
        can_execute = os.access(directory, os.X_OK)

        print(f"   Pode ler: {'✅' if can_read else '❌'}")
        print(f"   Pode escrever: {'✅' if can_write else '❌'}")
        print(f"   Pode executar: {'✅' if can_execute else '❌'}")

        # Lista arquivos dentro
        if os.path.isdir(directory):
            files = os.listdir(directory)
            print(f"   Arquivos: {len(files)} arquivo(s)")

            if files:
                print("   Conteúdo:")
                for f in files[:10]:  # Mostra até 10 arquivos
                    file_path = os.path.join(directory, f)
                    file_st = os.stat(file_path)
                    file_perms = stat.filemode(file_st.st_mode)
                    size = file_st.st_size
                    print(f"      - {f} ({file_perms}, {size} bytes)")

                if len(files) > 10:
                    print(f"      ... e mais {len(files) - 10} arquivo(s)")

        return can_read and can_write

    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")
        return False


def fix_permissions():
    """Tenta corrigir as permissões do diretório do banco"""
    persist_dir = get_persist_dir()

    print_header("Corrigindo Permissões")

    if not os.path.exists(persist_dir):
        print(f"📁 Criando diretório: {persist_dir}")
        os.makedirs(persist_dir, exist_ok=True)

    try:
        _ensure_directory_permissions(persist_dir)
        print("✅ Permissões corrigidas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao corrigir permissões: {e}")
        return False


def delete_and_recreate():
    """Remove o banco e recria o diretório"""
    persist_dir = get_persist_dir()

    print_header("Removendo e Recriando Banco")

    if os.path.exists(persist_dir):
        try:
            response = input(
                f"⚠️  Tem certeza que deseja remover o banco em '{persist_dir}'? (s/N): "
            )
            if response.lower() != "s":
                print("❌ Operação cancelada")
                return False

            delete_vector_store()
            print("✅ Banco removido com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
            return False

    # Recria o diretório
    try:
        os.makedirs(persist_dir, exist_ok=True)
        _ensure_directory_permissions(persist_dir)
        print(f"✅ Diretório recriado: {persist_dir}")
        return True
    except Exception as e:
        print(f"❌ Erro ao recriar diretório: {e}")
        return False


def main():
    """Função principal"""
    print_header("Diagnóstico e Correção do ChromaDB")

    persist_dir = get_persist_dir()
    print(f"📍 Diretório do banco: {persist_dir}")

    # Menu de opções
    while True:
        print("\nOpções:")
        print("1. Verificar permissões")
        print("2. Corrigir permissões")
        print("3. Testar banco existente")
        print("4. Remover e recriar banco (CUIDADO!)")
        print("5. Sair")

        choice = input("\nEscolha uma opção (1-5): ").strip()

        if choice == "1":
            print_header("Verificando Permissões")
            check_directory_permissions(persist_dir)

        elif choice == "2":
            fix_permissions()

        elif choice == "3":
            print_header("Testando Banco Existente")
            vector_store = check_and_repair_vector_store()
            if vector_store:
                print("✅ Banco está funcionando corretamente!")
            else:
                print("❌ Banco não existe ou está corrompido")

        elif choice == "4":
            delete_and_recreate()

        elif choice == "5":
            print("\n👋 Até logo!")
            break

        else:
            print("❌ Opção inválida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
