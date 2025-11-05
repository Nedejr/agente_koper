"""
Agente Koper - Streamlit Application
Chat RAG com LangGraph Agent + OpenRouter + Qdrant
"""

import asyncio
import os
import sys
import time

# Adiciona o diretório raiz ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from backend.config import settings
from backend.rag.document_processor import document_processor
from backend.rag.indexer import indexer
from backend.rag.retriever import retriever
from backend.agent.graph import run_agent

# Configuração da página
st.set_page_config(
    page_title="Agente Koper",
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
    
    if "documents_count" not in st.session_state:
        st.session_state["documents_count"] = 0
    
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = settings.openrouter_default_model


def render_sidebar():
    """Renderiza a barra lateral com controles"""
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        # Info do sistema
        with st.expander("ℹ️ Sistema", expanded=False):
            st.caption(f"**Versão:** {settings.app_version}")
            st.caption(f"**Ambiente:** {settings.environment}")
            st.caption(f"**LLM:** OpenRouter")
            st.caption(f"**Embeddings:** {settings.embeddings_model.split('/')[-1]}")
        
        st.divider()
        
        # Seleção de modelo
        st.header("🤖 Modelo")
        
        # Define modelos disponíveis com nomes amigáveis
        models_dict = {
            "meta-llama/llama-3.1-8b-instruct:free": "⭐ Meta Llama 3.1 8B (Recomendado)",
            "google/gemma-2-9b-it:free": "⭐ Google Gemma 2 9B (Recomendado)",
            "mistralai/mistral-7b-instruct:free": "Mistral 7B",
            "qwen/qwen-2.5-7b-instruct:free": "Qwen 2.5 7B",
            "microsoft/phi-3-medium-128k-instruct:free": "Microsoft Phi-3 Medium",
            "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free": "Nous Hermes 2 Mixtral",
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
            "meta-llama/llama-3.1-8b-instruct:free": "Excelente para conversação e atendimento. Contexto: 128k tokens",
            "google/gemma-2-9b-it:free": "Ótimo raciocínio e instruções complexas. Contexto: 8k tokens",
            "mistralai/mistral-7b-instruct:free": "Compacto e eficiente para RAG. Contexto: 32k tokens",
            "qwen/qwen-2.5-7b-instruct:free": "Bom balanço qualidade/velocidade. Contexto: 32k tokens",
            "microsoft/phi-3-medium-128k-instruct:free": "Grande contexto, ótimo para documentos. Contexto: 128k tokens",
            "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free": "Poderoso, mas mais lento. Contexto: 32k tokens",
        }
        st.caption(model_info.get(selected_model_name, ""))
        
        st.divider()
        
        # Seção de upload de arquivos
        st.header("📄 Upload de Documentos")
        uploaded_files = st.file_uploader(
            "Faça upload de arquivos",
            type=["pdf", "txt", "md", "markdown"],
            accept_multiple_files=True,
            help="Selecione arquivos PDF, TXT ou Markdown para indexar no sistema RAG",
        )
        
        if uploaded_files:
            if st.button("🚀 Processar e Indexar", type="primary", use_container_width=True):
                process_and_index_documents(uploaded_files)
        
        st.divider()
        
        # Estatísticas do índice
        render_index_stats()
        
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


def process_and_index_documents(uploaded_files):
    """Processa e indexa documentos no Qdrant"""
    with st.spinner("🔄 Processando e indexando documentos..."):
        try:
            total_chunks = 0
            
            for file in uploaded_files:
                # Lê o arquivo
                file_content = file.read()
                
                # Indexa usando o novo sistema
                result = asyncio.run(
                    indexer.index_uploaded_file(
                        file_content=file_content,
                        filename=file.name,
                    )
                )
                
                if result["status"] == "success":
                    total_chunks += result["chunks_indexed"]
                    st.session_state["documents_count"] += 1
                else:
                    st.error(f"❌ Erro ao processar {file.name}: {result.get('error')}")
            
            if total_chunks > 0:
                st.success(
                    f"""
                ✅ **Documentos indexados com sucesso!**
                - Arquivos: {len(uploaded_files)}
                - Chunks criados: {total_chunks}
                - Total de documentos: {st.session_state['documents_count']}
                """
                )
        
        except Exception as e:
            st.error(f"❌ Erro ao processar documentos: {str(e)}")


def render_index_stats():
    """Renderiza estatísticas do índice Qdrant"""
    st.header("📊 Estatísticas")
    
    try:
        stats = asyncio.run(indexer.get_index_stats())
        
        if stats["total_points"] > 0:
            st.metric("Chunks Indexados", stats["total_points"])
            st.caption(f"📁 Collection: {stats['collection_name']}")
            st.caption(f"✅ Status: {stats['status']}")
        else:
            st.info("Nenhum documento indexado ainda")
    
    except Exception as e:
        st.warning(f"Não foi possível obter estatísticas: {str(e)}")


def show_detailed_stats():
    """Mostra estatísticas detalhadas em um modal"""
    try:
        stats = asyncio.run(indexer.get_index_stats())
        
        st.sidebar.json({
            "collection": stats["collection_name"],
            "total_points": stats["total_points"],
            "status": stats["status"],
            "documents": st.session_state.get("documents_count", 0),
            "model": st.session_state.get("selected_model", "default"),
        })
    except Exception as e:
        st.sidebar.error(f"Erro: {str(e)}")


def render_chat_interface():
    """Renderiza a interface principal de chat"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💬 Agente Koper")
        st.caption("Assistente Inteligente com RAG + LangGraph + OpenRouter")
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
        
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(content)
        
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.write(content)
                
                # Mostra metadados se disponíveis
                if decision or sources or confidence or model_used:
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
    
    # Input de pergunta
    question = st.chat_input("Como posso ajudar?")
    
    if question:
        handle_user_question(question)


def handle_user_question(question: str):
    """Processa a pergunta usando o LangGraph Agent"""
    # Adiciona pergunta ao histórico
    st.session_state["messages"].append({"role": "user", "content": question})
    
    # Mostra a pergunta
    with st.chat_message("user", avatar="👤"):
        st.write(question)
    
    # Gera resposta usando o agente
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Pensando..."):
            try:
                # Executa o agente LangGraph
                start_time = time.time()
                
                agent_result = asyncio.run(
                    run_agent(
                        user_message=question,
                        conversation_id=st.session_state["conversation_id"],
                        selected_model=st.session_state.get("selected_model")
                    )
                )
                
                processing_time = time.time() - start_time
                
                # Extrai informações do resultado
                response = agent_result.get("response", "Desculpe, não consegui gerar uma resposta.")
                decision = agent_result.get("agent_decision")
                sources = agent_result.get("sources", [])
                confidence = agent_result.get("evaluator_confidence")
                steps = agent_result.get("processing_steps", [])
                model_used = st.session_state.get("selected_model")
                
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
                    
                    if steps:
                        st.caption(f"🔄 **Passos:** {' → '.join(steps)}")
                    
                    st.caption(f"⏱️ **Tempo:** {processing_time:.2f}s")
                
                # Adiciona resposta ao histórico
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": response,
                    "decision": decision,
                    "sources": sources,
                    "confidence": confidence,
                    "model": model_used,
                })
            
            except Exception as e:
                error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": error_msg,
                })


def render_welcome_message():
    """Renderiza mensagem de boas-vindas quando não há mensagens"""
    if not st.session_state.get("messages"):
        st.markdown("""
        ## 👋 Bem-vindo ao Agente Koper!
        
        ### Como usar:
        
        1. **🤖 Selecione um modelo** na barra lateral (todos gratuitos!)
        2. **📄 Faça upload de documentos** sobre o Koper ERP
        3. **🚀 Processe e indexe** os arquivos
        4. **💬 Faça perguntas** sobre o conteúdo
        
        ### Recursos:
        
        - ✅ **OpenRouter**: Acesso a múltiplos modelos gratuitos
        - ✅ **RAG Inteligente**: Busca semântica em seus documentos
        - ✅ **LangGraph Agent**: Roteamento inteligente de respostas
        - ✅ **Qdrant**: Vector store de alta performance
        
        ### Modelos Disponíveis (Gratuitos):
        
        - **⭐ Meta Llama 3.1 8B** - Melhor para conversação
        - **⭐ Google Gemma 2 9B** - Ótimo raciocínio
        - **Mistral 7B** - Eficiente para RAG
        - **Microsoft Phi-3** - Grande contexto (128k tokens)
        - **E mais...**
        
        ### Tipos de resposta:
        
        - **✅ Resposta**: Informação encontrada nos documentos
        - **🤝 Atendimento Humano**: Informação insuficiente
        - **🚫 Fora do Escopo**: Pergunta não relacionada ao Koper ERP
        
        ---
        
        **Comece selecionando um modelo e fazendo upload de documentos!** 👉
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
