"""
Módulo responsável pelo sistema de Q&A usando RAG
"""

import re
from typing import List, Optional, Tuple

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import Config

# Prompt padrão do sistema
DEFAULT_SYSTEM_PROMPT = """
Você é um assistente chamado Agente Koper. Quando o chat iniciar se apresente de forma cordial e amigável.

Você responde perguntas baseado EXCLUSIVAMENTE no contexto fornecido.

Contexto: {context}

Regras CRÍTICAS - LEIA COM ATENÇÃO:
1. Use SOMENTE o contexto acima para responder.
2. Se não houver informação suficiente, diga: "Desculpe, não encontrei informações sobre isso na documentação disponível."
3. NUNCA invente informações.

REGRA OBRIGATÓRIA SOBRE MÍDIA (VÍDEOS E IMAGENS):
- O contexto contém tags de mídia no formato [image: nome-do-arquivo.png] e [video: nome-do-arquivo.mp4]
- PRIORIDADE: Você DEVE incluir APENAS UM VÍDEO por resposta, se existir vídeo relevante no contexto
- Se NÃO houver vídeo relevante, você DEVE incluir APENAS UMA IMAGEM, se existir imagem relevante no contexto
- NUNCA inclua vídeo E imagem juntos na mesma resposta
- NUNCA inclua mais de um vídeo ou mais de uma imagem
- Escolha o vídeo ou imagem MAIS relevante para a pergunta do usuário
- Você DEVE copiar a tag [video: ...] ou [image: ...] EXATAMENTE como está no contexto
- NÃO parafraseie, NÃO resuma, NÃO ignore - COPIE a tag EXATAMENTE
- Coloque a tag logo APÓS explicar o processo relacionado
- Exemplo com vídeo: "... siga estes passos no sistema.\n\n[video: Como Entregar o EPI ao Colaborador.mp4]\n\n"
- Exemplo com imagem (quando não há vídeo): "... clique em Entregar.\n\n[image: modal-entrega-de-epi.png]\n\n"

Mantenha um tom profissional e amigável. Formate sua resposta de forma clara.
"""


def build_prompt_with_history(
    system_prompt: str, chat_history: Optional[List[dict]] = None
) -> ChatPromptTemplate:
    """
    Constrói um prompt do ChatGPT incluindo histórico de conversa

    Args:
        system_prompt: Prompt do sistema
        chat_history: Lista de mensagens anteriores [{'role': 'user'/'ai', 'content': '...'}]

    Returns:
        ChatPromptTemplate configurado
    """
    messages = [("system", system_prompt)]

    if chat_history:
        for message in chat_history:
            role = message.get("role")
            content = message.get("content")

            # Converte role 'user' ou 'ai' para formato do langchain
            if role == "user":
                messages.append(("human", content))
            elif role == "ai":
                messages.append(("assistant", content))

    # Adiciona a pergunta atual
    messages.append(("human", "{input}"))

    return ChatPromptTemplate.from_messages(messages)


def _extract_image_tags(text: str) -> List[str]:
    """
    Extrai todas as tags de imagem do texto.
    
    Args:
        text: Texto contendo tags [image: filename.png]
    
    Returns:
        Lista de nomes de arquivos de imagem
    """
    pattern = r'\[image:\s*([^\]]+)\]'
    return re.findall(pattern, text)


def _extract_video_tags(text: str) -> List[str]:
    """
    Extrai todas as tags de vídeo do texto.
    
    Args:
        text: Texto contendo tags [video: filename.mp4]
    
    Returns:
        Lista de nomes de arquivos de vídeo
    """
    pattern = r'\[video:\s*([^\]]+)\]'
    return re.findall(pattern, text)


def _extract_media_tags(text: str) -> List[tuple]:
    """
    Extrai todas as tags de mídia (imagens e vídeos) do texto.
    
    Args:
        text: Texto contendo tags [image: ...] e [video: ...]
    
    Returns:
        Lista de tuplas (tipo, nome_arquivo) onde tipo é 'image' ou 'video'
    """
    media = []
    
    # Extrai imagens
    for img in _extract_image_tags(text):
        media.append(('image', img))
    
    # Extrai vídeos
    for video in _extract_video_tags(text):
        media.append(('video', video))
    
    return media


def _ensure_media_in_response(response: str, context_media: List[tuple]) -> str:
    """
    Garante que UMA mídia relevante do contexto esteja na resposta.
    PRIORIDADE: 1 vídeo > 1 imagem
    - Se houver vídeo no contexto, inclui APENAS o primeiro vídeo
    - Se NÃO houver vídeo, inclui APENAS a primeira imagem
    - Remove duplicatas e garante apenas uma mídia por resposta
    
    Args:
        response: Resposta gerada pelo modelo
        context_media: Lista de tuplas (tipo, nome_arquivo) encontradas no contexto
    
    Returns:
        Resposta com APENAS UMA mídia (1 vídeo ou 1 imagem), sem duplicatas
    """
    # Separa vídeos e imagens do contexto
    context_videos = [m for m in context_media if m[0] == 'video']
    context_images = [m for m in context_media if m[0] == 'image']
    
    # Determina qual mídia devemos garantir na resposta (prioridade: vídeo > imagem)
    priority_media = None
    if context_videos:
        # Se há vídeos no contexto, escolhe o primeiro
        priority_media = context_videos[0]
    elif context_images:
        # Se não há vídeos mas há imagens, escolhe a primeira
        priority_media = context_images[0]
    
    # Remove TODAS as tags de mídia da resposta para garantir apenas uma
    lines = response.split('\n')
    cleaned_lines = []
    found_priority_media = False
    
    for line in lines:
        # Verifica se a linha contém uma tag de imagem
        img_match = re.search(r'\[image:\s*([^\]]+)\]', line)
        if img_match:
            img_name = img_match.group(1).strip()
            # Só mantém se for a mídia prioritária E ainda não encontramos ela
            if priority_media and priority_media == ('image', img_name) and not found_priority_media:
                found_priority_media = True
                cleaned_lines.append(line)
            # Caso contrário, remove esta linha
            continue
        
        # Verifica se a linha contém uma tag de vídeo
        video_match = re.search(r'\[video:\s*([^\]]+)\]', line)
        if video_match:
            video_name = video_match.group(1).strip()
            # Só mantém se for a mídia prioritária E ainda não encontramos ela
            if priority_media and priority_media == ('video', video_name) and not found_priority_media:
                found_priority_media = True
                cleaned_lines.append(line)
            # Caso contrário, remove esta linha
            continue
        
        # Linha normal, adiciona
        cleaned_lines.append(line)
    
    response = '\n'.join(cleaned_lines)
    
    # Se a mídia prioritária não foi encontrada na resposta, adiciona ao final
    if priority_media and not found_priority_media:
        media_type, media_name = priority_media
        response += f"\n\n[{media_type}: {media_name}]\n"
    
    return response


def ask_question(
    query: str,
    vector_store: Chroma,
    model_name: str = None,
    chat_history: Optional[List[dict]] = None,
    system_prompt: str = None,
    temperature: float = None,
) -> dict:
    """
    Faz uma pergunta ao sistema RAG e anexa referências de imagem se encontradas.

    Args:
        query: Pergunta do usuário
        vector_store: Vector store com os documentos
        model_name: Nome do modelo OpenAI (opcional, usa default)
        chat_history: Histórico de conversa (opcional)
        system_prompt: Prompt customizado (opcional, usa default)
        temperature: Temperatura do modelo (opcional, usa default)

    Returns:
        Dicionário com a resposta e os documentos fonte.
    """
    # Usa valores padrão se não fornecidos
    if model_name is None:
        model_name = Config.DEFAULT_MODEL

    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    if temperature is None:
        temperature = Config.TEMPERATURE

    # Cria o modelo LLM
    llm = ChatOpenAI(model=model_name, temperature=temperature)

    # Cria o retriever
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": Config.K_RETRIEVER}
    )


    # Busca documentos relevantes
    docs = retriever.invoke(query)

    # Formata o contexto, incluindo as tags de imagem que já estão no conteúdo
    # O processamento em `processing.py` já substitui a sintaxe Markdown de imagem
    # por uma tag como `[image: nome-da-imagem.png]`.
    # Ao passar o page_content diretamente, garantimos que o LLM veja essas tags.
    # A formatação com "Fonte X" ajuda o modelo a contextualizar melhor.
    context_parts = []
    for i, doc in enumerate(docs):
        source_name = doc.metadata.get("source", "desconhecida")
        context_parts.append(
            f"---\nFonte {i+1} (de {source_name}):\n{doc.page_content}"
        )
    context = "\n\n".join(context_parts)

    # Escapa chaves em contexto/histórico/pergunta para evitar erros de str.format
    def _escape_braces(s: str) -> str:
        if not isinstance(s, str):
            return s
        return s.replace("{", "{{").replace("}", "}}")

    # Constrói as mensagens (insere contexto protegido)
    safe_context = _escape_braces(context)
    messages = [("system", system_prompt.replace("{context}", safe_context))]

    # Adiciona o histórico de conversa (se fornecido)
    # O histórico é mantido para preservar o contexto da conversa,
    # mas a cada nova pergunta o RAG busca novos documentos relevantes,
    # garantindo que as informações (incluindo imagens) sejam sempre atualizadas
    if chat_history:
        for message in chat_history:
            role = message.get("role")
            content = message.get("content")
            # Converte role 'user' ou 'ai' para formato do langchain
            if role == "user":
                messages.append(("human", _escape_braces(content)))
            elif role == "ai":
                messages.append(("assistant", _escape_braces(content)))

    # Adiciona a pergunta atual (escapando chaves)
    messages.append(("human", _escape_braces(query)))

    # Cria o prompt e executa
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})

    # Extrai as mídias do contexto (imagens e vídeos)
    context_media = _extract_media_tags(context)
    
    # Garante que as mídias relevantes estejam na resposta
    response = _ensure_media_in_response(response, context_media)

    return {"answer": response, "source_documents": docs}


def ask_question_with_sources(
    query: str,
    vector_store: Chroma,
    model_name: str = None,
    chat_history: Optional[List[dict]] = None,
    k: int = 4,
) -> Tuple[str, List[str]]:
    """
    Faz uma pergunta e retorna a resposta junto com as fontes (documentos recuperados)

    Args:
        query: Pergunta do usuário
        vector_store: Vector store com os documentos
        model_name: Nome do modelo OpenAI
        chat_history: Histórico de conversa
        k: Número de documentos a recuperar

    Returns:
        Tupla (resposta, lista_de_fontes)
    """
    # Busca documentos relevantes
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.get_relevant_documents(query)

    # Gera a resposta
    result = ask_question(query, vector_store, model_name, chat_history)
    answer = result["answer"]

    # Extrai o conteúdo dos documentos como fontes
    sources = [doc.page_content[:200] + "..." for doc in docs]

    return answer, sources
