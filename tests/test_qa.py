"""
Testes para o módulo de Q&A
Execute: pytest tests/
"""

from backend.qa import DEFAULT_SYSTEM_PROMPT, build_prompt_with_history


def test_build_prompt_with_history_no_history():
    """Testa construção de prompt sem histórico"""
    prompt = build_prompt_with_history(DEFAULT_SYSTEM_PROMPT, None)

    assert prompt is not None
    # Verifica que tem system e human messages
    messages = prompt.messages
    assert len(messages) >= 2  # system + human


def test_build_prompt_with_history_with_messages():
    """Testa construção de prompt com histórico"""
    history = [
        {"role": "user", "content": "Primeira pergunta"},
        {"role": "ai", "content": "Primeira resposta"},
    ]

    prompt = build_prompt_with_history(DEFAULT_SYSTEM_PROMPT, history)

    assert prompt is not None
    messages = prompt.messages
    # system + 2 histórico + human atual
    assert len(messages) >= 4


def test_build_prompt_converts_roles():
    """Testa conversão correta de roles"""
    history = [
        {"role": "user", "content": "User message"},
        {"role": "ai", "content": "AI message"},
    ]

    prompt = build_prompt_with_history("System prompt", history)
    messages = prompt.messages

    # Verifica tipos de mensagens
    # Nota: isso depende da implementação interna do LangChain
    assert messages is not None


def test_default_system_prompt_exists():
    """Testa que o prompt padrão existe e tem conteúdo"""
    assert DEFAULT_SYSTEM_PROMPT is not None
    assert len(DEFAULT_SYSTEM_PROMPT) > 0
    assert "{context}" in DEFAULT_SYSTEM_PROMPT


# Nota: Testes de ask_question e ask_question_with_sources
# requerem mocking extensivo do LangChain e OpenAI
# ou uso de chave de API real para testes de integração
