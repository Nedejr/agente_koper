"""
Agente Koper - Streamlit API Client
Interface que consome a API FastAPI do backend
"""

import os
import time
from typing import List

import requests
import streamlit as st

# Configuração
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Configuração da página
st.set_page_config(
    page_title="Agente Koper - API Client",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Inicializa as variáveis do session_state"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = f"conv-{int(time.time())}"
    
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = "meta-llama/llama-3.2-3b-instruct:free"


def check_api_health() -> dict:
    """Verifica se a API está acessível"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def upload_document_api(file_content: bytes, filename: str) -> dict:
    """Faz upload de um documento via API"""
    try:
        files = {"file": (filename, file_content)}
        response = requests.post(f"{API_URL}/api/documents/upload", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_documents_stats() -> dict:
    """Obtém estatísticas dos documentos via API"""
    try:
        response = requests.get(f"{API_URL}/api/documents/stats")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def ask_question_api(
    query: str, conversation_id: str, model: str = None
) -> dict:
    """Faz uma pergunta à API e retorna a resposta completa do agente"""
    payload = {
        "message": query,
        "conversation_id": conversation_id,
        "user_id": "streamlit_user",
        "model": model,  # Modelo selecionado
    }

    response = requests.post(f"{API_URL}/api/chat", json=payload)
    response.raise_for_status()
    return response.json()


def render_sidebar():
    """Renderiza a barra lateral com controles"""
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        # Info do sistema
        with st.expander("ℹ️ Sistema", expanded=False):
            health = check_api_health()
            if health.get("status") == "healthy":
                st.success("✅ API conectada")
                st.caption(f"**Versão:** {health.get('version', 'N/A')}")
                st.caption(f"**Backend:** {API_URL}")
                st.caption(f"**LLM:** OpenRouter")
            else:
                st.error("❌ API desconectada")
                st.caption(f"URL: {API_URL}")
                if "error" in health:
                    st.caption(f"Erro: {health['error']}")
                st.stop()
        
        st.divider()
        
        # Seleção de modelo
        st.header("🤖 Modelo")
        
        # Define modelos disponíveis com nomes amigáveis
        models_dict = {
            "meta-llama/llama-3.2-3b-instruct:free": "⭐ Meta Llama 3.2 3B (Recomendado)",
            "meta-llama/llama-3.2-1b-instruct:free": "Meta Llama 3.2 1B (Rápido)",
            "google/gemma-2-9b-it:free": "⭐ Google Gemma 2 9B (Poderoso)",
            "mistralai/mistral-7b-instruct:free": "Mistral 7B",
            "qwen/qwen-2-7b-instruct:free": "Qwen 2 7B",
            "microsoft/phi-3-mini-128k-instruct:free": "Microsoft Phi-3 Mini",
        }
        
        # Modelo selecionado
        selected_model_name = st.selectbox(
            "Selecione o modelo OpenRouter",
            options=list(models_dict.keys()),
            format_func=lambda x: models_dict[x],
            index=0,
            help="Escolha o modelo de IA (todos são gratuitos)",
            key="model_selector"
        )
        st.session_state["selected_model"] = selected_model_name
        
        # Mostra info do modelo
        model_info = {
            "meta-llama/llama-3.2-3b-instruct:free": "Rápido e eficiente para conversação. Contexto: 128k tokens",
            "meta-llama/llama-3.2-1b-instruct:free": "Muito rápido, ideal para respostas simples. Contexto: 128k tokens",
            "google/gemma-2-9b-it:free": "Ótimo raciocínio e instruções complexas. Contexto: 8k tokens",
            "mistralai/mistral-7b-instruct:free": "Compacto e eficiente para RAG. Contexto: 32k tokens",
            "qwen/qwen-2-7b-instruct:free": "Bom balanço qualidade/velocidade. Contexto: 32k tokens",
            "microsoft/phi-3-mini-128k-instruct:free": "Grande contexto, compacto. Contexto: 128k tokens",
        }
        st.caption(model_info.get(selected_model_name, ""))
        
        st.divider()
        
        # Seção de upload de arquivos
        st.header("📄 Upload de Documentos")
        uploaded_files = st.file_uploader(
            "Faça upload de arquivos",
            type=["pdf", "txt", "md", "markdown"],
            accept_multiple_files=True,
            help="Selecione arquivos PDF, TXT ou Markdown para indexar no RAG",
        )
        
        if uploaded_files:
            if st.button("🚀 Processar e Indexar", type="primary", use_container_width=True):
                upload_documents(uploaded_files)
        
        st.divider()
        
        # Estatísticas
        render_stats()
        
        st.divider()
        
        # Botões de controle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar Chat", use_container_width=True):
                st.session_state["messages"] = []
                st.session_state["conversation_id"] = f"conv-{int(time.time())}"
                st.rerun()
        
        with col2:
            if st.button("📊 Ver Stats", use_container_width=True):
                show_detailed_stats()


def upload_documents(uploaded_files):
    """Faz upload de documentos via API"""
    with st.spinner("🔄 Enviando documentos para a API..."):
        total_files = len(uploaded_files)
        successful = 0
        failed = 0
        
        progress_bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            # Lê o conteúdo
            file_content = file.read()
            
            # Faz upload via API
            result = upload_document_api(file_content, file.name)
            
            if "error" not in result:
                successful += 1
                st.success(f"✅ {file.name}: {result.get('chunks_indexed', 0)} chunks")
            else:
                failed += 1
                st.error(f"❌ {file.name}: {result['error']}")
            
            # Atualiza progress bar
            progress_bar.progress((i + 1) / total_files)
    
    st.success(
        f"""
    ✅ **Processamento concluído!**
    - Total: {total_files}
    - Sucesso: {successful}
    - Falhas: {failed}
    """
    )


def render_stats():
    """Renderiza estatísticas dos documentos"""
    st.header("📊 Estatísticas")
    
    stats = get_documents_stats()
    
    if "error" not in stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documentos", stats.get("total_documents", 0))
        with col2:
            st.metric("Chunks", stats.get("total_chunks", 0))
        
        st.caption(f"📁 Collection: {stats.get('collection_name', 'N/A')}")
    else:
        st.warning("Não foi possível carregar estatísticas")


def show_detailed_stats():
    """Mostra estatísticas detalhadas"""
    stats = get_documents_stats()
    if "error" not in stats:
        st.sidebar.json(stats)
    else:
        st.sidebar.error(f"Erro: {stats['error']}")


def render_chat_interface():
    """Renderiza a interface principal de chat"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💬 Agente Koper - API Client")
        st.caption("Assistente Inteligente via FastAPI + OpenRouter")
    with col2:
        if st.button("🔄 Nova Conversa"):
            st.session_state["messages"] = []
            st.session_state["conversation_id"] = f"conv-{int(time.time())}"
            st.rerun()
    
    # Renderiza mensagens do histórico
    for message in st.session_state.get("messages", []):
        role = message.get("role")
        content = message.get("content")
        decision = message.get("decision")
        sources = message.get("sources")
        confidence = message.get("confidence")
        model_used = message.get("model")
        processing_time = message.get("processing_time_ms")
        
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(content)
        
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(content)
                
                # Mostra metadados
                if decision or sources or confidence or processing_time or model_used:
                    with st.expander("📋 Detalhes", expanded=False):
                        if model_used:
                            model_name = model_used.split('/')[-1].split(':')[0]
                            st.caption(f"🤖 Modelo: **{model_name}**")
                        
                        if decision:
                            decision_emoji = {
                                "answer": "✅",
                                "human_handoff": "🤝",
                                "off_topic": "🚫"
                            }.get(decision, "ℹ️")
                            st.caption(f"{decision_emoji} Decisão: **{decision}**")
                        
                        if confidence is not None:
                            st.caption(f"📊 Confiança: **{confidence:.2%}**")
                        
                        if sources:
                            st.caption("📚 Fontes:")
                            for source in sources:
                                st.caption(f"  • {source}")
                        
                        if processing_time:
                            st.caption(f"⏱️ Tempo: **{processing_time}ms**")
    
    # Input de pergunta
    question = st.chat_input("Como posso ajudar?")
    
    if question:
        handle_user_question(question)


def handle_user_question(question: str):
    """Processa a pergunta enviando para a API"""
    # Adiciona pergunta ao histórico
    st.session_state["messages"].append({"role": "user", "content": question})
    
    # Mostra a pergunta
    with st.chat_message("user", avatar="👤"):
        st.write(question)
    
    # Gera resposta usando a API
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Consultando o agente via API..."):
            try:
                start_time = time.time()
                
                # Chama a API
                agent_result = ask_question_api(
                    query=question,
                    conversation_id=st.session_state["conversation_id"],
                    model=st.session_state.get("selected_model")
                )
                
                processing_time = time.time() - start_time
                
                # Extrai informações do resultado
                response = agent_result.get("response", "Desculpe, não consegui gerar uma resposta.")
                decision = agent_result.get("decision")
                sources = agent_result.get("sources", [])
                confidence = agent_result.get("confidence")
                model_used = st.session_state.get("selected_model")
                api_processing_time = agent_result.get("processing_time_ms")
                
                # Mostra resposta
                st.write(response)
                
                # Mostra detalhes
                with st.expander("📋 Detalhes da Resposta", expanded=False):
                    if model_used:
                        model_name = model_used.split('/')[-1].split(':')[0]
                        st.caption(f"🤖 **Modelo:** {model_name}")
                    
                    if decision:
                        decision_emoji = {
                            "answer": "✅",
                            "human_handoff": "🤝",
                            "off_topic": "🚫"
                        }.get(decision, "ℹ️")
                        st.caption(f"{decision_emoji} **Decisão:** {decision}")
                    
                    if confidence is not None:
                        st.caption(f"📊 **Confiança:** {confidence:.2%}")
                    
                    if sources:
                        st.caption("📚 **Fontes:**")
                        for source in sources:
                            st.caption(f"  • {source}")
                    
                    if api_processing_time:
                        st.caption(f"⏱️ **Tempo (API):** {api_processing_time}ms")
                    
                    st.caption(f"⏱️ **Tempo (Total):** {processing_time:.2f}s")
                
                # Adiciona resposta ao histórico
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": response,
                    "decision": decision,
                    "sources": sources,
                    "confidence": confidence,
                    "model": model_used,
                    "processing_time_ms": api_processing_time,
                })
            
            except Exception as e:
                error_msg = f"❌ Erro ao chamar API: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": error_msg,
                })


def render_welcome_message():
    """Renderiza mensagem de boas-vindas quando não há mensagens"""
    if not st.session_state.get("messages"):
        st.markdown("""
        ## 👋 Bem-vindo ao Agente Koper API Client!
        
        ### Como usar:
        
        1. **🤖 Selecione um modelo** na barra lateral (todos gratuitos!)
        2. **📄 Faça upload de documentos** sobre o Koper ERP
        3. **🚀 Processe e indexe** os arquivos
        4. **💬 Faça perguntas** sobre o conteúdo
        
        ### Recursos:
        
        - ✅ **OpenRouter**: Acesso a múltiplos modelos gratuitos
        - ✅ **API Backend**: FastAPI + LangGraph + RAG
        - ✅ **Qdrant**: Vector store de alta performance
        - ✅ **Seleção de Modelos**: Escolha entre 6 modelos gratuitos
        
        ### Modelos Disponíveis (Gratuitos):
        
        - **⭐ Meta Llama 3.1 8B** - Melhor para conversação (128k contexto)
        - **⭐ Google Gemma 2 9B** - Ótimo raciocínio (8k contexto)
        - **Mistral 7B** - Eficiente para RAG (32k contexto)
        - **Qwen 2.5 7B** - Bom balanço (32k contexto)
        - **Microsoft Phi-3 Medium** - Grande contexto (128k tokens)
        - **Nous Hermes 2 Mixtral** - Poderoso (32k contexto)
        
        ### Tipos de resposta:
        
        - **✅ Resposta**: Informação encontrada nos documentos
        - **🤝 Atendimento Humano**: Informação insuficiente
        - **🚫 Fora do Escopo**: Pergunta não relacionada ao Koper ERP
        
        ---
        
        **Comece selecionando um modelo e fazendo uma pergunta!** 👉
        """)


def main():
    """Função principal da aplicação"""
    try:
        # Inicializa session state
        initialize_session_state()
        
        # Renderiza interface
        render_sidebar()
        
        # Se não há mensagens, mostra boas-vindas
        if not st.session_state.get("messages"):
            render_welcome_message()
        
        # Renderiza chat
        render_chat_interface()
    
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
