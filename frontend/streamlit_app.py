"""
Aplicação Streamlit para Chat RAG com documentos PDF
"""

# Fallback para sqlite3 (necessário em alguns ambientes como Streamlit Cloud)
import os
import sys

# Adiciona o diretório raiz ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import streamlit as st

from backend.config import Config
from backend.processing import get_document_stats, process_multiple_pdfs
from backend.qa import ask_question
from backend.vector_store import (
    add_to_vector_store,
    delete_vector_store,
    get_vector_store_stats,
    load_existing_vector_store,
)

# Configuração da página
st.set_page_config(page_title="Chat RAG - Documentos", page_icon="🤖", layout="wide")


def initialize_session_state():
    """Inicializa as variáveis do session_state"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = load_existing_vector_store()

    if "documents_loaded" not in st.session_state:
        st.session_state["documents_loaded"] = False


def render_sidebar():
    """Renderiza a barra lateral com controles"""
    with st.sidebar:
        st.title("⚙️ Configurações")

        # Seção de upload de arquivos
        st.header("📄 Upload de Documentos")
        uploaded_files = st.file_uploader(
            "Faça upload de arquivos PDF",
            type=["pdf"],
            accept_multiple_files=True,
            help="Selecione um ou mais arquivos PDF para processar",
        )

        if uploaded_files:
            if st.button("🚀 Processar Documentos", type="primary"):
                process_documents(uploaded_files)

        st.divider()

        # Seleção de modelo
        st.header("🤖 Modelo")
        selected_model = st.selectbox(
            "Selecione o modelo OpenAI",
            Config.AVAILABLE_MODELS,
            index=0,
            help="Escolha o modelo de IA para responder suas perguntas",
        )
        st.session_state["selected_model"] = selected_model

        # Configuração de temperatura
        temperature = st.slider(
            "🌡️ Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=Config.TEMPERATURE,
            step=0.1,
            help="Controla a criatividade das respostas (0 = mais focado, 1 = mais criativo)",
        )
        st.session_state["temperature"] = temperature

        st.divider()

        # Estatísticas do vector store
        render_vector_store_stats()

        st.divider()

        # Botão para limpar histórico e vector store
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Chat"):
                st.session_state["messages"] = []
                st.rerun()

        with col2:
            if st.button("⚠️ Resetar DB"):
                reset_database()


def process_documents(uploaded_files):
    """Processa os documentos enviados"""
    with st.spinner("🔄 Processando documentos..."):
        try:
            # Processa os PDFs
            chunks = process_multiple_pdfs(uploaded_files)

            # Obtém estatísticas
            stats = get_document_stats(chunks)

            # Adiciona ao vector store
            st.session_state["vector_store"] = add_to_vector_store(
                chunks, st.session_state["vector_store"]
            )

            st.session_state["documents_loaded"] = True

            # Mostra sucesso
            st.success(
                f"""
            ✅ **Documentos processados com sucesso!**
            - Arquivos: {len(uploaded_files)}
            - Chunks: {stats['total_chunks']}
            - Caracteres: {stats['total_characters']:,}
            - Tamanho médio: {stats['avg_chunk_size']} caracteres
            """
            )

        except Exception as e:
            st.error(f"❌ Erro ao processar documentos: {str(e)}")


def render_vector_store_stats():
    """Renderiza estatísticas do vector store"""
    st.header("📊 Estatísticas")

    stats = get_vector_store_stats(st.session_state.get("vector_store"))

    if stats["exists"]:
        st.metric("Documentos no DB", stats.get("total_documents", "N/A"))
        st.caption(f"📁 {stats.get('persist_directory', 'N/A')}")
    else:
        st.info("Nenhum documento carregado ainda")


def reset_database():
    """Reseta o banco de dados vetorial"""
    if st.session_state.get("vector_store"):
        try:
            delete_vector_store()
            st.session_state["vector_store"] = None
            st.session_state["documents_loaded"] = False
            st.session_state["messages"] = []
            st.success("✅ Database resetado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao resetar database: {str(e)}")


def render_chat_interface():
    """Renderiza a interface principal de chat"""
    st.title("💬 Chat com seus Documentos (RAG)")
    st.caption("Faça perguntas sobre os documentos carregados")

    # Renderiza mensagens do histórico
    for message in st.session_state.get("messages", []):
        role = message.get("role")
        content = message.get("content")

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(content)
        elif role == "ai":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(content)

    # Input de pergunta
    question = st.chat_input("Como posso ajudar?")

    if question:
        handle_user_question(question)


def handle_user_question(question: str):
    """Processa a pergunta do usuário"""
    vector_store = st.session_state.get("vector_store")

    if not vector_store:
        st.warning("⚠️ Por favor, carregue documentos primeiro!")
        return

    # Adiciona pergunta ao histórico
    st.session_state["messages"].append({"role": "user", "content": question})

    # Mostra a pergunta
    with st.chat_message("user", avatar="👤"):
        st.write(question)

    # Gera resposta
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Pensando..."):
            try:
                # Pega configurações
                model_name = st.session_state.get(
                    "selected_model", Config.DEFAULT_MODEL
                )
                temperature = st.session_state.get("temperature", Config.TEMPERATURE)

                # Histórico (sem a pergunta atual)
                chat_history = st.session_state["messages"][:-1]

                # Gera resposta
                response = ask_question(
                    query=question,
                    vector_store=vector_store,
                    model_name=model_name,
                    chat_history=chat_history,
                    temperature=temperature,
                )

                # Mostra resposta
                st.write(response)

                # Adiciona resposta ao histórico
                st.session_state["messages"].append({"role": "ai", "content": response})

            except Exception as e:
                error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append(
                    {"role": "ai", "content": error_msg}
                )


def main():
    """Função principal da aplicação"""
    try:
        # Valida configurações
        Config.validate()

        # Inicializa session state
        initialize_session_state()

        # Renderiza interface
        render_sidebar()
        render_chat_interface()

    except ValueError as e:
        st.error(f"⚠️ Erro de configuração: {str(e)}")
        st.info("Por favor, configure a variável OPENAI_API_KEY no arquivo .env")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    main()
