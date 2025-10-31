"""
Módulo responsável pelo sistema de Q&A usando RAG
"""

from typing import List, Optional, Tuple

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import Config

# Prompt padrão do sistema
DEFAULT_SYSTEM_PROMPT = """
Você é um assistente útil que responde perguntas baseado no contexto fornecido.

Use o contexto abaixo para responder as perguntas de forma precisa e objetiva.

Contexto: {context}

Regras:
- Se a resposta estiver no contexto, forneça uma resposta clara e direta
- Se não houver informação suficiente no contexto, diga claramente que não há informação disponível
- Não invente informações que não estejam no contexto
- Cite trechos relevantes do contexto quando apropriado
- Mantenha um tom profissional e amigável
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


def ask_question(
    query: str,
    vector_store: Chroma,
    model_name: str = None,
    chat_history: Optional[List[dict]] = None,
    system_prompt: str = None,
    temperature: float = None,
) -> str:
    """
    Faz uma pergunta ao sistema RAG

    Args:
        query: Pergunta do usuário
        vector_store: Vector store com os documentos
        model_name: Nome do modelo OpenAI (opcional, usa default)
        chat_history: Histórico de conversa (opcional)
        system_prompt: Prompt customizado (opcional, usa default)
        temperature: Temperatura do modelo (opcional, usa default)

    Returns:
        Resposta gerada pelo modelo
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
    retriever = vector_store.as_retriever()

    # Busca documentos relevantes
    docs = retriever.invoke(query)

    # Formata o contexto
    context = "\n\n".join([doc.page_content for doc in docs])

    # Constrói as mensagens
    messages = [("system", system_prompt.replace("{context}", context))]

    # Adiciona histórico
    if chat_history:
        for message in chat_history:
            role = message.get("role")
            content = message.get("content")
            if role == "user":
                messages.append(("human", content))
            elif role == "ai":
                messages.append(("assistant", content))

    # Adiciona a pergunta atual
    messages.append(("human", query))

    # Cria o prompt e executa
    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})

    return response


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
    answer = ask_question(query, vector_store, model_name, chat_history)

    # Extrai o conteúdo dos documentos como fontes
    sources = [doc.page_content[:200] + "..." for doc in docs]

    return answer, sources
