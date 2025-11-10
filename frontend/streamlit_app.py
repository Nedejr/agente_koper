"""
Aplicação Streamlit para Chat RAG com documentos (PDF, TXT, Markdown)
"""

import json
import os
import re
import sys
from io import BytesIO

import streamlit as st

# Adiciona o diretório raiz ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

from backend.config import Config
from backend.processing import get_document_stats, process_multiple_files
from backend.qa import ask_question
from backend.vector_store import (
    add_to_vector_store,
    delete_vector_store,
    get_vector_store_stats,
    load_existing_vector_store,
)

# Configuração da página
st.set_page_config(page_title="Chat RAG - Documentos", page_icon="🤖", layout="wide")


@st.cache_data
def load_image_map():
    """Carrega o mapeamento de imagens do arquivo JSON."""
    try:
        map_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs-gestao-epi",
            "images_map.json",
        )
        with open(map_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar o mapa de imagens: {e}")
        return {}


@st.cache_data
def load_video_map():
    """Carrega o mapeamento de vídeos do arquivo JSON."""
    try:
        map_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs-gestao-epi",
            "videos_map.json",
        )
        with open(map_path, "r") as f:
            return json.load(f)
    except Exception:
        # Se não houver arquivo de vídeos, retorna dicionário vazio (não é erro crítico)
        return {}


def load_default_documents():
    """Carrega os documentos padrão da pasta docs-gestao-epi"""
    with st.spinner("🔄 Carregando documentos padrão..."):
        try:
            doc_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "docs-gestao-epi",
                "gestao_epi_documentacao.md",
            )

            if os.path.exists(doc_path):
                with open(doc_path, "rb") as f:
                    file_like = BytesIO(f.read())
                    file_like.name = os.path.basename(doc_path)
                    process_documents([file_like])
            else:
                st.error("❌ Documento padrão não encontrado!")

        except Exception as e:
            st.error(f"❌ Erro ao carregar documentos padrão: {str(e)}")


def initialize_session_state():
    """Inicializa as variáveis do session_state"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = load_existing_vector_store()

    if "documents_loaded" not in st.session_state:
        st.session_state["documents_loaded"] = False

    if not st.session_state["vector_store"]:
        load_default_documents()


def render_sidebar():
    """Renderiza a barra lateral com controles"""
    with st.sidebar:
        st.title("⚙️ Configurações")
        st.header("📄 Documentos")
        st.info("Utilizando a documentação padrão de gestão de EPI.")
        st.divider()
        st.header("🤖 Modelo")
        selected_model = st.selectbox(
            "Selecione o modelo OpenAI",
            Config.AVAILABLE_MODELS,
            index=0,
            help="Escolha o modelo de IA para responder suas perguntas",
        )
        st.session_state["selected_model"] = selected_model
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
        render_vector_store_stats()
        st.divider()
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
            chunks = process_multiple_files(uploaded_files)
            stats = get_document_stats(chunks)
            st.session_state["vector_store"] = add_to_vector_store(
                chunks, st.session_state["vector_store"]
            )
            st.session_state["documents_loaded"] = True

            # Armazena estatísticas do processamento
            st.session_state["last_processing_stats"] = {
                "files_count": len(uploaded_files),
                "total_chunks": stats["total_chunks"],
                "total_characters": stats["total_characters"],
                "avg_chunk_size": stats["avg_chunk_size"],
            }

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

        # Mostra estatísticas detalhadas do último processamento
        if "last_processing_stats" in st.session_state:
            proc_stats = st.session_state["last_processing_stats"]
            st.divider()
            st.success("✅ Documentos processados com sucesso!")
            st.markdown(
                f"""
**Arquivos:** {proc_stats['files_count']}  
**Chunks:** {proc_stats['total_chunks']}  
**Caracteres:** {proc_stats['total_characters']:,}  
**Tamanho médio:** {proc_stats['avg_chunk_size']} caracteres
            """
            )
    else:
        st.info("Nenhum documento carregado ainda")


def reset_database():
    """Reseta o banco de dados vetorial, remove arquivos corrompidos e recarrega documentos"""
    try:
        with st.spinner("🔄 Resetando banco de dados..."):
            # Passo 1: Limpa o session state
            st.session_state["vector_store"] = None
            st.session_state["documents_loaded"] = False
            st.session_state["messages"] = []

            # Passo 2: Remove o diretório do banco completamente
            try:
                delete_vector_store()
                st.info("✅ Banco de dados removido")
            except Exception as delete_error:
                st.warning(f"⚠️ Aviso ao remover DB: {delete_error}")
                # Tenta forçar a remoção mesmo com erro
                import shutil

                persist_dir = Config.PERSIST_DIR
                if os.path.exists(persist_dir):
                    try:
                        # Tenta mudar permissões antes de remover
                        import stat

                        for root, dirs, files in os.walk(persist_dir):
                            for d in dirs:
                                os.chmod(os.path.join(root, d), stat.S_IRWXU)
                            for f in files:
                                os.chmod(os.path.join(root, f), stat.S_IRWXU)
                        shutil.rmtree(persist_dir)
                        st.info("✅ Banco removido forçadamente")
                    except Exception as force_error:
                        st.error(f"❌ Não foi possível remover: {force_error}")

            # Passo 3: Recarrega os documentos padrão
            st.info("📄 Recarregando documentos...")
            load_default_documents()

        st.success("✅ Database resetado e documentos recarregados com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Erro ao resetar database: {str(e)}")
        st.info(
            "💡 Tente fechar o Streamlit, remover manualmente a pasta 'chroma_db' e reiniciar."
        )


def render_message(content: str, image_map: dict, video_map: dict):
    """Renderiza a mensagem, substituindo tags de imagem e vídeo por mídias reais."""
    # Regex para encontrar tags de mídia [image: ...] e [video: ...]
    media_regex = r"\[(image|video):\s*([^\]]+)\]"
    parts = re.split(media_regex, content)

    i = 0
    while i < len(parts):
        part = parts[i]

        # Verifica se é uma tag de mídia
        if i > 0 and i % 3 == 1:  # É o tipo de mídia (image ou video)
            media_type = part
            media_name = parts[i + 1].strip() if i + 1 < len(parts) else ""

            if media_type == "image":
                image_path = image_map.get(media_name)
                if image_path and os.path.exists(image_path):
                    # Exibe a imagem usando st.image com opção de expandir
                    st.image(
                        image_path,
                        caption=media_name,
                        width=400,
                    )
                    # Adiciona um botão para visualizar em tamanho real
                    with st.expander("🔍 Clique para ver em tamanho real"):
                        st.image(image_path, caption=media_name)
                else:
                    st.warning(f"⚠️ Imagem não encontrada: {media_name}")

            elif media_type == "video":
                video_path = video_map.get(media_name)
                if video_path and os.path.exists(video_path):
                    # Exibe o vídeo usando st.video com largura de 80%
                    col1, col2, col3 = st.columns([0.10, 0.80, 0.10])
                    with col2:
                        st.video(video_path)
                        st.caption(f"📹 {media_name}")
                # Se o vídeo não existir, simplesmente não exibe nada (ignora silenciosamente)

            i += 2  # Pula o nome da mídia
        elif part.strip() and i % 3 == 0:
            # É texto normal
            st.write(part)

        i += 1


def render_chat_interface():
    """Renderiza a interface principal de chat"""
    st.title("💬 Agente Koper")
    st.caption("Faça perguntas sobre os documentos carregados")
    image_map = load_image_map()
    video_map = load_video_map()

    # Mensagem de boas-vindas se não houver mensagens
    if not st.session_state.get("messages", []):
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(
                """
👋 **Olá! Eu sou o Agente Koper!**

Estou aqui para ajudá-lo com dúvidas sobre **Gestão de EPI** (Equipamentos de Proteção Individual).

Posso te auxiliar com:
- 📦 Como cadastrar um novo EPI
- 📥 Registrar entrada de EPIs no estoque
- 📤 Fazer entregas de EPI aos colaboradores
- 🔄 Transferir EPIs entre locais
- ↩️ Processar devoluções de EPI
- 🗑️ Dar baixa em EPIs danificados ou vencidos
- 📊 Gerar relatórios de movimentações
- ❌ Cancelar entregas de EPI

💡 **Dica:** Posso mostrar vídeos tutoriais para te guiar passo a passo!

Como posso ajudar você hoje?
            """
            )

    for message in st.session_state.get("messages", []):
        role = message.get("role")
        content = message.get("content")
        with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
            render_message(content, image_map, video_map)

    question = st.chat_input("Como posso ajudar?")
    if question:
        handle_user_question(question, image_map, video_map)


def handle_user_question(question: str, image_map: dict, video_map: dict):
    """Processa a pergunta do usuário"""
    vector_store = st.session_state.get("vector_store")
    if not vector_store:
        st.warning("⚠️ Por favor, carregue documentos primeiro!")
        return

    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.write(question)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Pensando..."):
            try:
                model_name = st.session_state.get(
                    "selected_model", Config.DEFAULT_MODEL
                )
                temperature = st.session_state.get("temperature", Config.TEMPERATURE)
                chat_history = st.session_state["messages"][:-1]

                result = ask_question(
                    query=question,
                    vector_store=vector_store,
                    model_name=model_name,
                    chat_history=chat_history,
                    temperature=temperature,
                )

                response_text = result["answer"]
                render_message(response_text, image_map, video_map)
                st.session_state["messages"].append(
                    {"role": "ai", "content": response_text}
                )

            except Exception as e:
                error_msg = f"❌ Erro ao gerar resposta: {str(e)}"
                st.error(error_msg)
                st.session_state["messages"].append(
                    {"role": "ai", "content": error_msg}
                )


def main():
    """Função principal da aplicação"""
    try:
        Config.validate()
        initialize_session_state()
        render_sidebar()
        render_chat_interface()
    except ValueError as e:
        st.error(f"⚠️ Erro de configuração: {str(e)}")
        st.info("Por favor, configure a variável OPENAI_API_KEY no arquivo .env")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    main()
