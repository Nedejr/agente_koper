"""
Frontend Streamlit que consome a API FastAPI
Use este arquivo quando o backend estiver rodando como API separada
"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List

import requests
import streamlit as st

# Configuração da API
API_URL = st.secrets.get("API_URL", "http://localhost:8000")


# Configuração da página
st.set_page_config(page_title="Chat RAG - API Client", page_icon="🤖", layout="wide")


def initialize_session_state():
    """Inicializa as variáveis do session_state"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


def check_api_health() -> bool:
    """Verifica se a API está acessível"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def upload_documents(files) -> dict:
    """Faz upload de documentos para a API"""
    files_data = []
    for file in files:
        files_data.append(("files", (file.name, file.getvalue(), "application/pdf")))

    response = requests.post(f"{API_URL}/upload", files=files_data)
    response.raise_for_status()
    return response.json()


def ask_question_api(
    query: str, model: str, temperature: float, history: List[dict]
) -> str:
    """Faz uma pergunta à API"""
    payload = {
        "query": query,
        "model": model,
        "temperature": temperature,
        "history": history,
    }

    response = requests.post(f"{API_URL}/ask", json=payload)
    response.raise_for_status()
    return response.json()["answer"]


def get_stats() -> dict:
    """Obtém estatísticas da API"""
    response = requests.get(f"{API_URL}/stats")
    response.raise_for_status()
    return response.json()


def reset_database():
    """Reseta o database via API"""
    response = requests.delete(f"{API_URL}/reset")
    response.raise_for_status()
    return response.json()


def get_available_models() -> dict:
    """Obtém modelos disponíveis da API"""
    response = requests.get(f"{API_URL}/models")
    response.raise_for_status()
    return response.json()


def render_sidebar():
    """Renderiza a barra lateral com controles"""
    with st.sidebar:
        st.title("⚙️ Configurações")

        # Status da API
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API Conectada")
        else:
            st.error(f"❌ API não acessível em {API_URL}")
            st.stop()

        st.divider()

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
                process_documents_api(uploaded_files)

        st.divider()

        # Seleção de modelo
        st.header("🤖 Modelo")
        try:
            models_data = get_available_models()
            available_models = models_data.get("models", ["gpt-3.5-turbo"])
        except Exception:
            available_models = ["gpt-3.5-turbo"]

        selected_model = st.selectbox(
            "Selecione o modelo OpenAI",
            available_models,
            index=0,
            help="Escolha o modelo de IA para responder suas perguntas",
        )
        st.session_state["selected_model"] = selected_model

        # Configuração de temperatura
        temperature = st.slider(
            "🌡️ Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controla a criatividade das respostas",
        )
        st.session_state["temperature"] = temperature

        st.divider()

        # Estatísticas
        render_stats()

        st.divider()

        # Botões de controle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Chat"):
                st.session_state["messages"] = []
                st.rerun()

        with col2:
            if st.button("⚠️ Resetar DB"):
                reset_db_api()


def process_documents_api(uploaded_files):
    """Processa os documentos via API"""
    with st.spinner("🔄 Processando documentos..."):
        try:
            result = upload_documents(uploaded_files)

            st.success(
                f"""
            ✅ **Documentos processados com sucesso!**
            - Arquivos: {result['files_processed']}
            - Chunks: {result['total_chunks']}
            - Caracteres: {result['stats']['total_characters']:,}
            """
            )

        except Exception as e:
            st.error(f"❌ Erro ao processar documentos: {str(e)}")


def render_stats():
    """Renderiza estatísticas do vector store"""
    st.header("📊 Estatísticas")

    try:
        stats = get_stats()

        if stats["exists"]:
            st.metric("Documentos no DB", stats.get("total_documents", "N/A"))
            st.caption(f"📁 {stats.get('persist_directory', 'N/A')}")
        else:
            st.info("Nenhum documento carregado ainda")
    except Exception:
        st.warning("Não foi possível carregar estatísticas")


def reset_db_api():
    """Reseta o database via API"""
    try:
        reset_database()
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
    """Processa a pergunta do usuário via API"""
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
                model_name = st.session_state.get("selected_model", "gpt-3.5-turbo")
                temperature = st.session_state.get("temperature", 0.7)

                # Histórico (sem a pergunta atual)
                chat_history = st.session_state["messages"][:-1]

                # Gera resposta via API
                response = ask_question_api(
                    query=question,
                    model=model_name,
                    temperature=temperature,
                    history=chat_history,
                )

                # Mostra resposta
                st.write(response)

                # Adiciona resposta ao histórico
                st.session_state["messages"].append({"role": "ai", "content": response})

            except requests.exceptions.HTTPError as e:
                error_msg = f"❌ Erro HTTP: {e.response.status_code} - {e.response.json().get('detail', str(e))}"
                st.error(error_msg)
            except Exception as e:
                error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                st.error(error_msg)


def main():
    """Função principal da aplicação"""
    try:
        # Inicializa session state
        initialize_session_state()

        # Renderiza interface
        render_sidebar()
        render_chat_interface()

    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    main()
