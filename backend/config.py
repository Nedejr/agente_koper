"""
Configurações centralizadas do backend
"""

import os

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class Config:
    """Classe de configuração centralizada"""

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # ChromaDB
    PERSIST_DIR = os.getenv("PERSIST_DIR", "db")

    # Modelos disponíveis
    AVAILABLE_MODELS = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
    DEFAULT_MODEL = "gpt-3.5-turbo"

    # Processamento de documentos
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "400"))

    # Temperatura do modelo
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

    @classmethod
    def validate(cls):
        """Valida se as configurações obrigatórias estão presentes"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada no .env")
        return True


# Configura a chave da OpenAI no ambiente
if Config.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
