"""
Testes para o módulo de configuração
Execute: pytest tests/
"""

import os

import pytest

from backend.config import Config


def test_config_has_required_attributes():
    """Testa se Config tem os atributos necessários"""
    assert hasattr(Config, "OPENAI_API_KEY")
    assert hasattr(Config, "PERSIST_DIR")
    assert hasattr(Config, "AVAILABLE_MODELS")
    assert hasattr(Config, "DEFAULT_MODEL")
    assert hasattr(Config, "CHUNK_SIZE")
    assert hasattr(Config, "CHUNK_OVERLAP")
    assert hasattr(Config, "TEMPERATURE")


def test_default_values():
    """Testa valores padrão das configurações"""
    assert Config.DEFAULT_MODEL in Config.AVAILABLE_MODELS
    assert Config.CHUNK_SIZE > 0
    assert Config.CHUNK_OVERLAP >= 0
    assert 0.0 <= Config.TEMPERATURE <= 1.0


def test_persist_dir_default():
    """Testa valor padrão do diretório de persistência"""
    if "PERSIST_DIR" not in os.environ:
        assert Config.PERSIST_DIR == "db"


def test_available_models():
    """Testa lista de modelos disponíveis"""
    assert isinstance(Config.AVAILABLE_MODELS, list)
    assert len(Config.AVAILABLE_MODELS) > 0
    assert "gpt-3.5-turbo" in Config.AVAILABLE_MODELS


def test_validate_raises_without_key():
    """Testa se validate() levanta erro sem chave OpenAI"""
    original_key = Config.OPENAI_API_KEY
    Config.OPENAI_API_KEY = None

    with pytest.raises(ValueError, match="OPENAI_API_KEY não configurada"):
        Config.validate()

    # Restaura valor original
    Config.OPENAI_API_KEY = original_key


def test_validate_passes_with_key():
    """Testa se validate() passa com chave OpenAI configurada"""
    if Config.OPENAI_API_KEY:
        assert Config.validate()
    else:
        pytest.skip("OPENAI_API_KEY não configurada no ambiente de teste")
